import os

from common.browser import launch_browser
from common.logger import log

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

try:
    log("Opening MC-GUI with Playwright Inspector")

    page.goto(
        "https://10.130.209.10:8443/Margin_Calculator_Jenkins_git/",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.pause()

finally:
    browser.close()
    playwright.stop()