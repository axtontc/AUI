import asyncio
import json
import os
import time
from typing import Any, Dict, Optional
from playwright.async_api import Page

from telemetry import get_tracer


class AUIController:
    """
    Executive router that coordinates browser-use and desktop automation.
    Resolves native dialog locations from shadow_dom.json and triggers clicks/typing.
    """

    def __init__(self, shadow_dom_path: str = "shadow_dom.json") -> None:
        self.shadow_dom_path = os.path.abspath(shadow_dom_path)
        self.lock_path = self.shadow_dom_path + ".lock"

    def read_state(self) -> Dict[str, Any]:
        """Reads the shadow DOM state safely using a shared file lock."""
        if not os.path.exists(self.shadow_dom_path):
            return {}

        from filelock import FileLock, Timeout

        lock = FileLock(self.lock_path)
        tracer = get_tracer()

        with tracer.start_as_current_span("aui_controller.read_state") as span:
            try:
                with lock.acquire(timeout=0.2):
                    with open(self.shadow_dom_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        span.set_attribute("status", "success")
                        if isinstance(data, dict):
                            return data
                        return {}
            except (Timeout, json.JSONDecodeError, FileNotFoundError) as e:
                span.set_attribute("status", "failed")
                span.record_exception(e)
                return {}

    def get_element_by_class(
        self, window_title_query: str, class_name_query: str, name_query: Optional[str] = None
    ) -> Optional[Dict[str, int]]:
        """Queries shadow_dom.json to find a child control by class and optionally name."""
        tracer = get_tracer()
        with tracer.start_as_current_span("aui_controller.get_element_by_class") as span:
            span.set_attribute("window_title_query", window_title_query)
            span.set_attribute("class_name_query", class_name_query)
            if name_query:
                span.set_attribute("name_query", name_query)

            state = self.read_state()
            windows = state.get("windows", {})

            for win_id, win in windows.items():
                if window_title_query.lower() in win.get("title", "").lower():
                    for el in win.get("elements", []):
                        if class_name_query.lower() in el.get("class_name", "").lower():
                            if name_query is None or name_query.lower() in el.get("name", "").lower():
                                rect = el.get("rect")
                                if rect and len(rect) == 4:
                                    x = int(rect[0] + (rect[2] - rect[0]) / 2)
                                    y = int(rect[1] + (rect[3] - rect[1]) / 2)
                                    span.set_attribute("match_found", True)
                                    return {"x": x, "y": y}
            span.set_attribute("match_found", False)
            return None

    def get_element_coords(self, window_title_query: str, element_name_query: str) -> Optional[Dict[str, int]]:
        """Queries shadow_dom.json to find element center (x, y) coordinates by element name."""
        tracer = get_tracer()
        with tracer.start_as_current_span("aui_controller.get_element_coords") as span:
            span.set_attribute("window_title_query", window_title_query)
            span.set_attribute("element_name_query", element_name_query)

            state = self.read_state()
            windows = state.get("windows", {})

            for win_id, win in windows.items():
                if window_title_query.lower() in win.get("title", "").lower():
                    if element_name_query.lower() in win.get("title", "").lower():
                        rect = win.get("rect")
                        if rect and len(rect) == 4:
                            span.set_attribute("match_found", True)
                            return {
                                "x": int(rect[0] + (rect[2] - rect[0]) / 2),
                                "y": int(rect[1] + (rect[3] - rect[1]) / 2),
                            }
                    for el in win.get("elements", []):
                        if element_name_query.lower() in el.get("name", "").lower():
                            rect = el.get("rect")
                            if rect and len(rect) == 4:
                                span.set_attribute("match_found", True)
                                return {
                                    "x": int(rect[0] + (rect[2] - rect[0]) / 2),
                                    "y": int(rect[1] + (rect[3] - rect[1]) / 2),
                                }
            span.set_attribute("match_found", False)
            return None

    def physical_click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
        """Executes a PyAutoGUI mouse click at exact screen coordinates."""
        import pyautogui

        pyautogui.FAILSAFE = False
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)

    def physical_type(self, text: str) -> None:
        """Executes a PyAutoGUI typewrite with character intervals."""
        import pyautogui

        pyautogui.FAILSAFE = False
        pyautogui.write(text, interval=0.01)

    def physical_hotkey(self, keys_str: str) -> None:
        """Executes a PyAutoGUI hotkey sequence."""
        import pyautogui

        pyautogui.FAILSAFE = False
        keys = [k.strip() for k in keys_str.split(",")]
        pyautogui.hotkey(*keys)

    def click_element(self, window_title: str, element_name: str) -> bool:
        """Clicks a native Windows UI element based on shadow DOM coordinates."""
        tracer = get_tracer()
        with tracer.start_as_current_span("aui_controller.click_element") as span:
            span.set_attribute("window_title", window_title)
            span.set_attribute("element_name", element_name)

            coords = self.get_element_coords(window_title, element_name)
            if not coords:
                span.set_attribute("status", "element_not_found")
                return False
            self.physical_click(coords["x"], coords["y"])
            span.set_attribute("status", "success")
            return True

    async def handle_file_chooser(self, page: Page, click_target: str, file_path: str) -> bool:
        """
        Playwright Hook connection wrapper.
        Sets up an expectation hook for a native FileChooser dialog,
        and falls back to ETW+PyAutoGUI if the native Playwright handler times out.
        """
        tracer = get_tracer()
        with tracer.start_as_current_span("aui_controller.handle_file_chooser") as span:
            span.set_attribute("click_target", click_target)
            span.set_attribute("file_path", file_path)

            async def wait_and_fill_dialog() -> bool:
                timeout = 10.0
                start = time.time()
                while time.time() - start < timeout:
                    dialog_coords = self.get_element_by_class("Open", "Edit")
                    if not dialog_coords:
                        dialog_coords = self.get_element_by_class("Select File", "Edit")

                    if dialog_coords:
                        self.physical_click(dialog_coords["x"], dialog_coords["y"])
                        time.sleep(0.1)
                        self.physical_hotkey("ctrl,a")
                        self.physical_type(os.path.abspath(file_path))
                        time.sleep(0.1)

                        open_btn = self.get_element_by_class("Open", "Button", name_query="Open")
                        if not open_btn:
                            open_btn = self.get_element_by_class("Open", "Button", name_query="&Open")

                        if open_btn:
                            self.physical_click(open_btn["x"], open_btn["y"])
                        else:
                            self.physical_hotkey("enter")
                        return True
                    await asyncio.sleep(0.2)
                return False

            task = asyncio.create_task(wait_and_fill_dialog())

            try:
                await page.evaluate(f"document.querySelector('{click_target}').click()")
            except Exception as e:
                span.record_exception(e)
                await page.click(click_target)

            success = await task
            span.set_attribute("status", "success" if success else "failed")
            return bool(success)
