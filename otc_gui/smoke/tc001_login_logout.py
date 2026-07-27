import os

from datetime import datetime

from common.login import login
from common.logout import logout
from common.browser import launch_browser
from common.report import generate_report
from common.screenshot import capture_screenshot
from common.logger import log


# Remove proxy settings inherited from the environment
for proxy in (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy"
):
    os.environ.pop(proxy, None)

os.environ["NO_PROXY"] = "10.130.209.10"
os.environ["no_proxy"] = "10.130.209.10"

playwright, browser, context, page = launch_browser()

page.on(
    "requestfailed",
    lambda request: log(f"FAILED: {request.url} - {request.failure}")
)

result = "FAILED"

try:

    login(page)

    page.wait_for_timeout(10000)

    logout(page)

    page.wait_for_timeout(10000)

    screenshot_path = capture_screenshot(
    page,
    "login_logout_success"
    )
    log(f"Screenshot saved: {screenshot_path}")

    result = "PASSED"

except Exception as e:

    result = f"FAILED - {e}"

finally:

    generate_report(
        "TC001_LOGIN_LOGOUT",
        result
    )

    log(f"Test Result: {result}")

    browser.close()
    playwright.stop()