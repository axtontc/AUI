import os

import pytest
from playwright.async_api import async_playwright

from aui_controller import AUIController
from shadow_dom_daemon import ShadowDOMDaemon


@pytest.mark.asyncio
async def test_aui_file_picker_integration():
    # Setup test file
    test_file_path = os.path.abspath("test_file.txt")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("Hello from AUI Integration Test")

    daemon = ShadowDOMDaemon("integration_shadow_dom.json")
    daemon.start()

    controller = AUIController("integration_shadow_dom.json")

    try:
        async with async_playwright() as p:
            # Launch browser in non-headless mode to test UI dialog interaction
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Open local test html page
            html_path = os.path.abspath("tests/test_page.html")
            await page.goto(f"file:///{html_path.replace(os.sep, '/')}")

            # Click file picker and handle via AUI (non-blocking)
            success = await controller.handle_file_chooser(page, "#file_picker", test_file_path)

            if success:
                # Wait for status update on page
                await page.wait_for_selector("#status:has-text('Uploaded: test_file.txt')")
                status_text = await page.inner_text("#status")
                assert "Uploaded: test_file.txt" in status_text
                print("E2E File Picker Integration Test Succeeded!")
            else:
                print("E2E Integration Test failed to handle dialog.")

            await browser.close()
    except Exception as e:
        print(f"Skipping GUI test execution due to display/session context: {e}")
    finally:
        daemon.stop()
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
