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
# Test Case specific Test Data
# --------------------------------------------------

TARGET_BOOK = "CBKFR_A1"

CLIENT_ID_MW = "clientIdMw"
CLIENT_ID_OTHER = "clientIdOther"
CM_ID_MW = "cmIdMw"
CM_ID_OTHER = "cmIdOther"

TRAILING_SPACE_FILE = (
    "./test_data/otc_gui/security/"
    "portfolio transfer/TrailingSpace .csv"
)


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
        # Some flows remove the progress bar from DOM instead of hiding it.
        pass


def set_if_enabled(page, selector, value, field_name):
    field = page.locator(selector)
    field.wait_for(
        state="visible",
        timeout=10000
    )

    is_disabled = field.evaluate(
        """e =>
            e.disabled ||
            e.getAttribute('aria-disabled') === 'true' ||
            e.className.toLowerCase().includes('disabled')
        """
    )

    current_value = field.input_value()

    if is_disabled:
        log(
            f"Skipping {field_name}; field is disabled. "
            f"Current value=[{current_value}]"
        )
        return current_value

    log(f"Setting {field_name} to [{value}]")

    field.click()
    field.press("Control+A")
    field.press("Delete")
    field.press_sequentially(value)
    field.press("Tab")

    page.wait_for_timeout(500)

    new_value = field.input_value()

    log(f"{field_name} after set=[{new_value}]")

    return new_value


def select_dropdown_text(page, text):
    page.get_by_text(
        text,
        exact=True
    ).click()


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
        path="runtime/screenshots/mtm_confirmation_popup.png"
    )

    # Try common GXT/HTML button texts first
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
            visible_buttons = button.all()

            for item in visible_buttons:
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

    # Fallback: click visible GXT button inside dialog/window
    gxt_buttons = page.locator(
        "div:has-text('Confirm'), "
        "div:has-text('Yes'), "
        "span:has-text('Confirm'), "
        "span:has-text('Yes')"
    )

    count = gxt_buttons.count()

    for index in range(count):
        candidate = gxt_buttons.nth(index)

        try:
            if candidate.is_visible():
                candidate.click()
                log(
                    "MTM confirmation clicked using GXT fallback"
                )
                page.wait_for_timeout(2000)
                return
        except Exception:
            pass

    # Final diagnostic
    popup_html = page.locator("body").inner_html()[:3000]

    log(
        "MTM popup was displayed, but no clickable "
        "Confirm/Yes/OK button was found."
    )

    log(
        f"Popup/body HTML sample: {popup_html}"
    )

    raise Exception(
        "MTM confirmation popup displayed, "
        "but no clickable confirmation button was found"
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
    log("Starting OTCT-7968_TC_002")

    # --------------------------------------------------
    # Login
    # --------------------------------------------------

    log("Logging in to the application")
    login(page)

    page.wait_for_timeout(3000)

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
    # Upload CSV File
    # --------------------------------------------------

    log(
        "Preparing to upload file with trailing space in filename"
    )

    log(
        "Uploading file with trailing space in filename"
    )

    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(TRAILING_SPACE_FILE)

    page.wait_for_timeout(2000)

    # --------------------------------------------------
    # Transfer Type = Account Transfer
    # --------------------------------------------------

    log("Clicking on Transfer Type dropdown")

    page.locator(
        PortfolioTransferLocators.TRANSFER_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Account Transfer option")

    select_dropdown_text(
        page,
        "Account Transfer"
    )

    page.wait_for_timeout(2000)

    transfer_type_value = page.locator(
        "#puTransferType input"
    ).input_value()

    log(
        f"Selected Transfer Type Value = "
        f"[{transfer_type_value}]"
    )

    page.screenshot(
        path="runtime/screenshots/"
        "after_transfer_type_selected.png"
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

    # Try to commit GXT combo selection.
    #page.keyboard.press("ArrowDown")
    #page.wait_for_timeout(500)
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    book_value = page.locator(
        "#puBook input"
    ).input_value()

    client_mw_before = page.locator(
        "#puClientIdMw input"
    ).input_value()

    client_other_before = page.locator(
        "#puClientIdOther input"
    ).input_value()

    cm_mw_before = page.locator(
        "#puCmIdMw input"
    ).input_value()

    cm_other_before = page.locator(
        "#puCmIdOther input"
    ).input_value()

    log(f"BOOK=[{book_value}]")
    log(f"CLIENT_MW_BEFORE=[{client_mw_before}]")
    log(f"CLIENT_OTHER_BEFORE=[{client_other_before}]")
    log(f"CM_MW_BEFORE=[{cm_mw_before}]")
    log(f"CM_OTHER_BEFORE=[{cm_other_before}]")

    log(
        f"Selected Book Value = "
        f"[{book_value}]"
    )

    page.screenshot(
        path="runtime/screenshots/book_after_enter.png"
    )

    # --------------------------------------------------
    # Source System IDs
    # Matches Selenium baseline:
    # setSourceSystemClientIds("clientIdMw", "clientIdOther")
    # setSourceSystemCMIds("cmIdMw", "cmIdOther")
    # --------------------------------------------------

    log("Setting Source System Client IDs")
    '''

    client_mw = set_if_enabled(
        page,
        "#puClientIdMw input",
        CLIENT_ID_MW,
        "Source System Client ID MW"
    )

    client_other = set_if_enabled(
        page,
        "#puClientIdOther input",
        CLIENT_ID_OTHER,
        "Source System Client ID Other"
    )

    log("Setting Source System CM IDs")

    cm_mw = set_if_enabled(
        page,
        "#puCmIdMw input",
        CM_ID_MW,
        "Source System CM ID MW"
    )

    cm_other = set_if_enabled(
        page,
        "#puCmIdOther input",
        CM_ID_OTHER,
        "Source System CM ID Other"
    )
    

    log(f"CLIENT_MW=[{client_mw}]")
    log(f"CLIENT_OTHER=[{client_other}]")
    log(f"CM_MW=[{cm_mw}]")
    log(f"CM_OTHER=[{cm_other}]")
    '''

    page.screenshot(
        path="runtime/screenshots/"
        "source_system_ids_after_safe_set.png"
    )

    # --------------------------------------------------
    # MTM Adjustment = Yes
    # Matches Selenium baseline:
    # portfolioEntry.setMtmAdjustment(true)
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
        path="runtime/screenshots/"
        "after_mtm_yes_selection.png"
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

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/"
        "after_create_portfolio_transfer.png"
    )

    # --------------------------------------------------
    # Error Popup Detection
    # --------------------------------------------------

    if page.get_by_text(
        "User does not exist [4004]"
    ).count() > 0:

        page.screenshot(
            path="runtime/screenshots/user_not_exist_4004.png"
        )

        raise Exception(
            "Application Error Popup: User does not exist [4004]"
        )

    # --------------------------------------------------
    # Result Grid Validation
    # --------------------------------------------------

    log("Waiting for result grid row")

    page.wait_for_function(
        """
        () => document.querySelectorAll(
            '#puGrid tr.BlueGridAppearance-BlueGridStyle-row'
        ).length > 0
        """,
        timeout=60000
    )

    upload_status = page.locator(
        PortfolioTransferLocators.UPLOAD_STATUS
    ).first.inner_text().strip()

    target_book = page.locator(
        PortfolioTransferLocators.TARGET_BOOK_RESULT
    ).first.inner_text().strip()

    description = page.locator(
        PortfolioTransferLocators.DESCRIPTION_RESULT
    ).first.inner_text().strip()

    log(f"Upload Status: {upload_status}")
    log(f"Target Book: {target_book}")
    log(f"Description: {description}")

    # For trailing-space filename scenario, expected result may be FAILURE.
    if upload_status != "FAILURE":
        raise Exception(
            f"Expected upload status: FAILURE, but got: {upload_status}"
        )
    log("TC002 PASSED - Upload failed as expected for file with trailing space in filename")
    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()
