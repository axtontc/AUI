import ctypes
import json
import logging
import multiprocessing
import os
import time
from typing import Any, Dict, Optional

from telemetry import get_tracer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AUI_Daemon")


# Win32 Structs
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


# Win32 APIs
EnumWindows = ctypes.windll.user32.EnumWindows
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetClassName = ctypes.windll.user32.GetClassNameW
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowRect = ctypes.windll.user32.GetWindowRect
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId


def get_window_details(hwnd: int) -> Dict[str, Any]:
    """Helper to extract details for a specific window/control handle."""
    class_name = ctypes.create_unicode_buffer(256)
    GetClassName(hwnd, class_name, 256)

    text_length = GetWindowTextLength(hwnd)
    text_buff = ctypes.create_unicode_buffer(text_length + 1)
    GetWindowText(hwnd, text_buff, text_length + 1)

    rect = RECT()
    GetWindowRect(hwnd, ctypes.byref(rect))

    pid = ctypes.c_ulong()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    return {
        "hwnd": hwnd,
        "pid": pid.value,
        "class": class_name.value,
        "text": text_buff.value,
        "rect": [rect.left, rect.top, rect.right, rect.bottom],
    }


class ShadowDOMDaemon:
    """
    Asynchronous background daemon running the Windows UIAutomation tracker.
    Dumps the active window tree (names, classes, control types, and coordinate boundaries)
    to a shared JSON file using a cross-process lock.
    """

    def __init__(self, output_path: str = "shadow_dom.json") -> None:
        self.output_path = os.path.abspath(output_path)
        self.lock_path = self.output_path + ".lock"
        self.running = False
        self.listener_process: Any = None

    def dump_state(self, state: Dict[str, Any]) -> None:
        """Writes current UI tree state to output_path using a file lock."""
        from filelock import FileLock, Timeout

        lock = FileLock(self.lock_path)
        tracer = get_tracer()

        with tracer.start_as_current_span("shadow_dom_daemon.dump_state") as span:
            span.set_attribute("output_path", self.output_path)
            start_time = time.perf_counter()
            try:
                with lock.acquire(timeout=0.2):
                    temp_path = self.output_path + ".tmp"
                    with open(temp_path, "w", encoding="utf-8") as f:
                        json.dump(state, f, indent=2)
                    if os.path.exists(self.output_path):
                        os.remove(self.output_path)
                    os.rename(temp_path, self.output_path)

                latency = (time.perf_counter() - start_time) * 1000
                span.set_attribute("latency_ms", latency)
                span.set_attribute("status", "success")
            except Timeout:
                span.set_attribute("status", "timeout")
                span.record_exception(TimeoutError("Lock acquisition timed out"))
            except Exception as e:
                span.set_attribute("status", "error")
                span.record_exception(e)
                logger.error(f"[!] Error dumping state: {e}")

    @staticmethod
    def _listener_loop(output_path: str, lock_path: str) -> None:
        """Core listener loop that runs in a background process."""
        from filelock import FileLock

        tracer = get_tracer()

        logger.info("ETW/Win32 ShadowDOM Daemon Loop Started.")
        known_state: Dict[str, Any] = {}

        while True:
            try:
                with tracer.start_as_current_span("shadow_dom_daemon.scan") as span:
                    windows = {}

                    def foreach_window(hwnd: int, lParam: int) -> bool:
                        if IsWindowVisible(hwnd):
                            details = get_window_details(hwnd)
                            if details["text"] and details["rect"][2] > details["rect"][0]:
                                children = []

                                def foreach_child(hwnd_child: int, lParam_child: int) -> bool:
                                    child_details = get_window_details(hwnd_child)
                                    children.append(
                                        {
                                            "name": child_details["text"],
                                            "class_name": child_details["class"],
                                            "rect": child_details["rect"],
                                        }
                                    )
                                    return True

                                EnumChildWindows(hwnd, EnumWindowsProc(foreach_child), 0)

                                windows[str(hwnd)] = {
                                    "pid": details["pid"],
                                    "title": details["text"],
                                    "class_name": details["class"],
                                    "rect": details["rect"],
                                    "elements": children,
                                }
                        return True

                    EnumWindows(EnumWindowsProc(foreach_window), 0)

                    current_state = {"windows": windows, "last_updated": time.time()}

                    span.set_attribute("windows_tracked", len(windows))

                    # Sig check and write
                    state_sig = {k: (v["title"], v["rect"]) for k, v in windows.items()}
                    if state_sig != known_state:
                        known_state = state_sig
                        lock = FileLock(lock_path)
                        with lock.acquire(timeout=0.2):
                            temp_path = output_path + ".tmp"
                            with open(temp_path, "w", encoding="utf-8") as f:
                                json.dump(current_state, f, indent=2)
                            if os.path.exists(output_path):
                                os.remove(output_path)
                            os.rename(temp_path, output_path)

                    time.sleep(0.2)
            except Exception as e:
                logger.error(f"Daemon error: {e}")
                time.sleep(1)

    def start(self) -> None:
        """Starts the background listening process."""
        self.running = True
        self.listener_process = multiprocessing.Process(
            target=self._listener_loop, args=(self.output_path, self.lock_path)
        )
        self.listener_process.daemon = True
        self.listener_process.start()
        logger.info(f"AUI Daemon started (writing to {self.output_path})")

    def stop(self) -> None:
        """Stops the daemon and cleans up lock files."""
        self.running = False
        if self.listener_process:
            self.listener_process.terminate()
            self.listener_process.join()
        for p in [self.output_path, self.lock_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        logger.info("AUI Daemon stopped.")


if __name__ == "__main__":
    daemon = ShadowDOMDaemon()
    daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
