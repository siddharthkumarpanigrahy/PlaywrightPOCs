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

MISSING_HEADER_FILE = (
    "./test_data/otc_gui/security/"
    "portfolio transfer/Portfolio_MissingHeader.csv"
)

EXPECTED_ERROR_SNIPPETS = [
    "Csv file headers error",
    "Required file header"
]


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

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
        path="runtime/screenshots/tc004_mtm_confirmation_popup.png"
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
        path="runtime/screenshots/tc004_mtm_popup_no_button_found.png"
    )

    raise Exception(
        "MTM confirmation popup displayed, "
        "but no clickable Confirm/Yes/OK button was found"
    )


def close_ok_popup_if_present(page):
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
                    log("Popup closed using OK button")
                    page.wait_for_timeout(1000)
                    return True
            except Exception:
                pass

    return False


def assert_validation_error(page, expected_snippets):
    body_text = page.locator("body").inner_text()

    log("VALIDATION BODY TEXT START")
    log(body_text[:3000])
    log("VALIDATION BODY TEXT END")

    missing_snippets = []

    for snippet in expected_snippets:
        if snippet not in body_text:
            missing_snippets.append(snippet)

    if missing_snippets:
        page.screenshot(
            path="runtime/screenshots/tc004_expected_error_not_found.png"
        )

        raise Exception(
            "Expected validation error was not found. "
            f"Missing snippets: {missing_snippets}"
        )

    page.screenshot(
        path="runtime/screenshots/tc004_missing_header_error_displayed.png"
    )

    log(
        "Expected missing-header validation error displayed"
    )

    close_ok_popup_if_present(page)


def check_storage_error_after_upload(page):
    if page.get_by_text(
        "File not found in storage",
        exact=False
    ).count() > 0:

        page.screenshot(
            path="runtime/screenshots/tc004_file_not_found_in_storage.png"
        )

        raise Exception(
            "File upload failed before header validation: "
            "File not found in storage"
        )


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
    log("Starting OTCT-7968_TC_004")

    if not os.path.exists(MISSING_HEADER_FILE):
        raise Exception(
            f"Missing test data file: {MISSING_HEADER_FILE}"
        )

    # --------------------------------------------------
    # Login
    # --------------------------------------------------

    log("Logging in to the application")
    login(page)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc004_after_login.png"
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
    # Upload Missing Header CSV File
    # --------------------------------------------------

    log("Preparing to upload missing-header file")

    log("Uploading missing-header file")

    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(MISSING_HEADER_FILE)

    page.wait_for_timeout(2000)

    check_storage_error_after_upload(page)

    page.screenshot(
        path="runtime/screenshots/tc004_after_missing_header_file_upload.png"
    )

    # --------------------------------------------------
    # Transfer Type = Account Transfer
    # --------------------------------------------------

    log("Clicking on Transfer Type dropdown")

    page.locator(
        PortfolioTransferLocators.TRANSFER_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Account Transfer option")

    page.get_by_text(
        "Account Transfer",
        exact=True
    ).click()

    page.wait_for_timeout(2000)

    transfer_type_value = page.locator(
        "#puTransferType input"
    ).input_value()

    log(
        f"Selected Transfer Type Value = "
        f"[{transfer_type_value}]"
    )

    # --------------------------------------------------
    # Book = CBKFR_A1
    # --------------------------------------------------

    log("Setting Book value")

    book_field = page.locator(
        PortfolioTransferLocators.BOOK_FIELD
    )

    book_field.click()
    book_field.press("Control+A")
    book_field.press("Delete")
    book_field.press_sequentially(TARGET_BOOK)

    page.wait_for_timeout(1000)

    book_field.press("Enter")

    page.wait_for_timeout(3000)

    book_value = page.locator(
        "#puBook input"
    ).input_value()

    client_mw = page.locator(
        "#puClientIdMw input"
    ).input_value()

    client_other = page.locator(
        "#puClientIdOther input"
    ).input_value()

    cm_mw = page.locator(
        "#puCmIdMw input"
    ).input_value()

    cm_other = page.locator(
        "#puCmIdOther input"
    ).input_value()

    log(f"BOOK=[{book_value}]")
    log(f"CLIENT_MW=[{client_mw}]")
    log(f"CLIENT_OTHER=[{client_other}]")
    log(f"CM_MW=[{cm_mw}]")
    log(f"CM_OTHER=[{cm_other}]")

    if book_value != TARGET_BOOK:
        raise Exception(
            f"Expected book [{TARGET_BOOK}], got [{book_value}]"
        )

    if not client_other:
        raise Exception(
            "Expected Client Other to be auto-populated"
        )

    if not cm_mw:
        raise Exception(
            "Expected CM MW to be auto-populated"
        )

    if not cm_other:
        raise Exception(
            "Expected CM Other to be auto-populated"
        )

    page.screenshot(
        path="runtime/screenshots/tc004_after_book_auto_population.png"
    )

    # --------------------------------------------------
    # MTM Adjustment = Yes
    # --------------------------------------------------

    log("Clicking on MTM Adjustment dropdown")

    page.locator(
        PortfolioTransferLocators.MTM_FIELD
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting MTM Adjustment = Yes")

    page.get_by_text(
        "Yes",
        exact=True
    ).click()

    page.wait_for_timeout(2000)

    mtm_value = page.locator(
        "#puMtmAdj input"
    ).input_value()

    log(f"MTM Adjustment selected=[{mtm_value}]")

    page.screenshot(
        path="runtime/screenshots/tc004_after_mtm_yes_selection.png"
    )

    # --------------------------------------------------
    # Create Portfolio Transfer
    # --------------------------------------------------

    log("Creating Portfolio Transfer")

    page.locator(
        PortfolioTransferLocators.CREATE_PORTFOLIO_TRANSFER
    ).click()

    page.wait_for_timeout(2000)

    confirm_mtm_if_present(page)

    wait_for_progress_bar_close(page)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc004_after_create_click.png"
    )

    # --------------------------------------------------
    # Validate Missing Header Error
    # --------------------------------------------------

    assert_validation_error(
        page,
        EXPECTED_ERROR_SNIPPETS
    )

    log(
        "TC004 PASSED - Missing header file was rejected "
        "with expected validation error"
    )

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()
