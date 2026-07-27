import os

from datetime import datetime

from common.login import login
from common.logout import logout
from common.browser import launch_browser
from common.report import generate_report


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
    lambda request: print(
        "FAILED:", request.url, request.failure
    )
)

result = "FAILED"

try:

    login(page)

    page.wait_for_timeout(10000)

    logout(page)

    page.wait_for_timeout(10000)

    page.screenshot(
        path="runtime/screenshots/login_logout_success.png"
    )

    result = "PASSED"

except Exception as e:

    result = f"FAILED - {e}"

finally:

    generate_report(
        "TC001_LOGIN_LOGOUT",
        result
    )

    print(result)

    browser.close()
    playwright.stop()