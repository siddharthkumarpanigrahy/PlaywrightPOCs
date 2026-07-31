import os

from common.login import login
from common.logout import logout
from common.browser import launch_browser
from common.logger import log
from locators.otc_gui.portfolio_transfer_locators import (
    PortfolioTransferLocators,
)


# --------------------------------------------------
# Environment / Proxy
# --------------------------------------------------

for proxy in (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy"
):
    os.environ.pop(proxy, None)

os.environ["NO_PROXY"] = "10.130.209.10"
os.environ["no_proxy"] = "10.130.209.10"

os.makedirs("runtime/screenshots", exist_ok=True)


# --------------------------------------------------
# Test Data
# --------------------------------------------------

TARGET_BOOK = "CBKFR_A1"

EMPTY_FILE = (
    "./test_data/otc_gui/security/"
    "portfolio transfer/EmptyFile.csv"
)

EXPECTED_ERROR_MESSAGE = "File not found in storage"


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def handle_error_popup(page, expected_message):
    log(f"Checking for error popup message: [{expected_message}]")

    error_message = page.get_by_text(
        expected_message,
        exact=False
    )

    if error_message.count() == 0:
        page.screenshot(
            path="runtime/screenshots/tc003_expected_error_popup_not_found.png"
        )

        body_text = page.locator("body").inner_text()

        log("BODY TEXT WHEN EXPECTED POPUP NOT FOUND START")
        log(body_text[:3000])
        log("BODY TEXT WHEN EXPECTED POPUP NOT FOUND END")

        raise Exception(
            f"Expected popup message not found: [{expected_message}]"
        )

    log(f"Expected popup message displayed: [{expected_message}]")

    page.screenshot(
        path="runtime/screenshots/tc003_file_not_found_popup.png"
    )

    ok_button = page.get_by_text(
        "OK",
        exact=True
    )

    if ok_button.count() == 0:
        ok_button = page.get_by_text(
            "Ok",
            exact=True
        )

    if ok_button.count() > 0:
        for item in ok_button.all():
            try:
                if item.is_visible():
                    item.click()
                    log("Error popup closed using OK button")
                    page.wait_for_timeout(1000)
                    return
            except Exception:
                pass

    raise Exception(
        "Error popup was displayed, but OK button was not clickable"
    )


def wait_for_progress_bar_close(page, timeout=30000):
    progress_bar = page.locator("#progressBar")

    try:
        progress_bar.wait_for(
            state="hidden",
            timeout=timeout
        )
    except Exception:
        pass


def confirm_mtm_if_present(page):
    mtm_popup_text = page.get_by_text(
        "You are about to initiate a transfer with",
        exact=False
    )

    if mtm_popup_text.count() == 0:
        log("No MTM confirmation popup displayed")
        return

    log("MTM confirmation popup displayed")

    page.screenshot(
        path="runtime/screenshots/tc003_mtm_confirmation_popup.png"
    )

    possible_buttons = [
        "Confirm",
        "Yes",
        "OK",
        "Ok"
    ]

    for button_text in possible_buttons:
        button = page.get_by_text(
            button_text,
            exact=True
        )

        if button.count() > 0:
            for item in button.all():
                try:
                    if item.is_visible():
                        item.click()
                        log(
                            f"MTM confirmation clicked using text: "
                            f"[{button_text}]"
                        )
                        page.wait_for_timeout(2000)
                        return
                except Exception:
                    pass

    gxt_buttons = page.locator(
        "div:has-text('Confirm'), "
        "div:has-text('Yes'), "
        "span:has-text('Confirm'), "
        "span:has-text('Yes')"
    )

    for index in range(gxt_buttons.count()):
        candidate = gxt_buttons.nth(index)

        try:
            if candidate.is_visible():
                candidate.click()
                log("MTM confirmation clicked using GXT fallback")
                page.wait_for_timeout(2000)
                return
        except Exception:
            pass

    page.screenshot(
        path="runtime/screenshots/tc003_mtm_popup_no_button_found.png"
    )

    raise Exception(
        "MTM confirmation popup displayed, "
        "but no clickable Confirm/Yes/OK button was found"
    )


def assert_error_message(page, expected_message):
    log(f"Validating error message [{expected_message}]")

    error_message = page.get_by_text(
        expected_message,
        exact=False
    )

    if error_message.count() == 0:
        page.screenshot(
            path="runtime/screenshots/tc003_expected_error_not_found.png"
        )

        body_text = page.locator("body").inner_text()

        log("BODY TEXT WHEN ERROR NOT FOUND START")
        log(body_text[:3000])
        log("BODY TEXT WHEN ERROR NOT FOUND END")

        raise Exception(
            f"Expected error message not found: [{expected_message}]"
        )

    page.screenshot(
        path="runtime/screenshots/tc003_empty_file_error_displayed.png"
    )

    log(
        f"Expected error message displayed: "
        f"[{expected_message}]"
    )

    # Try to close popup if an OK button exists.
    ok_button = page.get_by_text(
        "OK",
        exact=True
    )

    if ok_button.count() == 0:
        ok_button = page.get_by_text(
            "Ok",
            exact=True
        )

    if ok_button.count() > 0:
        for item in ok_button.all():
            try:
                if item.is_visible():
                    item.click()
                    log("Error popup closed using OK")
                    page.wait_for_timeout(1000)
                    return
            except Exception:
                pass

    log("Error message found, but OK button was not clicked")


# --------------------------------------------------
# Browser Launch
# --------------------------------------------------

playwright, browser, context, page = launch_browser()

page.on(
    "requestfailed",
    lambda request: log(
        f"FAILED: {request.url} - {request.failure}"
    )
)


try:
    log("Starting OTCT-7968_TC_003")

   

    # --------------------------------------------------
    # Login
    # --------------------------------------------------

    log("Logging in to the application")
    login(page)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc003_after_login.png"
    )

    # --------------------------------------------------
    # Navigate to Portfolio Transfer Entry
    # --------------------------------------------------

    log("Navigating to Portfolio Transfer menu")
    page.click("a[href='#portfolio']")

    page.wait_for_timeout(2000)

    log("Navigating to Portfolio Transfer Entry")

    page.locator(
        ".BlueTabPanelAppearance-BlueTabPanelStyle-tabStripText"
    ).filter(
        has_text="Portfolio Transfer Entry"
    ).first.click()

    page.wait_for_timeout(2000)

    # --------------------------------------------------
    # Entry Type = Portfolio Upload
    # --------------------------------------------------

    log("Clicking on Entry Type dropdown")

    page.locator(
        PortfolioTransferLocators.ENTRY_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Portfolio Upload")

    page.get_by_text(
        "Portfolio Upload",
        exact=True
    ).click()

    page.wait_for_timeout(2000)

    # --------------------------------------------------
    # Upload Empty CSV File
    # --------------------------------------------------

    log("Preparing to upload empty file")

    empty_file = (
        "./test_data/otc_gui/security/"
        "portfolio transfer/EmptyFile.csv"
    )

    log("Uploading empty file")

    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(empty_file)

    page.wait_for_timeout(2000)

    page.screenshot(
        path="runtime/screenshots/tc003_after_empty_file_upload.png"
    )

    handle_error_popup(
        page,
        EXPECTED_ERROR_MESSAGE
    )

    log(
        "TC003 PASSED - Empty file upload was rejected "
        "with expected validation popup"
    )

    logout(page)
    
except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()