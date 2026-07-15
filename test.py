
import os
from playwright.sync_api import sync_playwright

# Remove proxy settings inherited from the environment
for proxy in [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy"
]:
    os.environ.pop(proxy, None)

os.environ["NO_PROXY"] = "10.130.209.10"
os.environ["no_proxy"] = "10.130.209.10"

with sync_playwright() as p:

    browser = p.firefox.launch(
        headless=False
    )

    context = browser.new_context(
        ignore_https_errors=True
    )

    page = context.new_page()

    page.on(
        "requestfailed",
        lambda request: print(
            "FAILED:", request.url, request.failure
        )
    )

    result = "FAILED"

    try:

        print("Opening OTC GUI...")

        page.goto(
            "https://10.130.209.10:8443/OTC_GUI/",
            wait_until="domcontentloaded",
            timeout=120000
        )

        print("Page Loaded")
        print("Page Title:", page.title())

        page.locator(
            'xpath=//*[@id="x-auto-11-input"]'
        ).fill(
            "AAACLUCLR001"
        )

        page.locator(
            'xpath=//*[@id="x-auto-12-input"]'
        ).fill(
            "AAACLUCLR001"
        )

        print("Credentials entered")

        page.locator(
            'xpath=//*[@id="login"]'
        ).click()

        print("Login button clicked")

        page.wait_for_timeout(10000)

        page.screenshot(
            path="login_success.png"
        )

        result = "PASSED"

    except Exception as e:

        result = f"FAILED - {e}"

    finally:

        with open("report.txt", "w") as report:

            report.write("Smoke Test - Login\n")
            report.write(f"Status : {result}\n")

        print(result)

        browser.close()