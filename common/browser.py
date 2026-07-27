import os

from playwright.sync_api import (
    sync_playwright
)


def get_headless_mode():

    return (
        os.getenv(
            "HEADLESS",
            "false"
        ).lower() == "true"
    )


def launch_browser():

    playwright = sync_playwright().start()

    headless_mode = get_headless_mode()

    if headless_mode:
        print("Running in headless mode")
    else:
        print("Running in headed mode")

    browser = playwright.firefox.launch(
        headless=headless_mode
    )

    context = browser.new_context(
        ignore_https_errors=True
    )

    page = context.new_page()

    return playwright, browser, context, page