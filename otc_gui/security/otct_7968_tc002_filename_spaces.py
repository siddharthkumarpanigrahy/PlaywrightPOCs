import os
from playwright.sync_api import TimeoutError

from common.login import login
from common.logout import logout
from common.browser import launch_browser
from common.logger import log
from locators.otc_gui.portfolio_transfer_locators import (
    PortfolioTransferLocators,
)

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
    lambda request: log(
        f"FAILED: {request.url} - {request.failure}"
    )
)

try:

    log("Starting OTCT-7968_TC_002")

    # Login
    log("Logging in to the application")
    login(page)

    page.wait_for_timeout(3000)

    # Portfolio Transfer menu
    log("Navigating to Portfolio Transfer menu")
    page.click("a[href='#portfolio']")

    page.wait_for_timeout(2000)

    # Portfolio Transfer Entry
    log("Navigating to Portfolio Transfer Entry")

    page.locator(
        ".BlueTabPanelAppearance-BlueTabPanelStyle-tabStripText"
    ).filter(
        has_text="Portfolio Transfer Entry"
    ).first.click()

    page.wait_for_timeout(2000)

    # Entry Type
    log("Clicking on Entry Type dropdown")

    page.locator(
        PortfolioTransferLocators.ENTRY_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Portfolio Upload")

    page.get_by_text(
        "Portfolio Upload"
    ).click()

    page.wait_for_timeout(2000)

    # Upload file
    log(
        "Preparing to upload file with trailing space in filename"
    )

    trailing_space_file = (
        "./test_data/otc_gui/security/"
        "portfolio transfer/TrailingSpace .csv"
    )

    log(
        "Uploading file with trailing space in filename"
    )

    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(trailing_space_file)

    page.wait_for_timeout(2000)

    # Transfer Type
    log("Clicking on Transfer Type dropdown")

    page.locator(
        PortfolioTransferLocators.TRANSFER_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Account Transfer option")

    page.locator(
        PortfolioTransferLocators.ACCOUNT_TRANSFER_OPTION
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
    # BOOK (Follow Java implementation)
    # --------------------------------------------------

    log("Setting Book value")

    book_field = page.locator(
        PortfolioTransferLocators.BOOK_FIELD
    )

    book_field.clear()
    book_field.fill("CBKFR_A1")
    book_field.press("Enter")

    page.wait_for_timeout(5000)

    book_value = page.locator(
        "#puBook input"
    ).input_value()

    log(
        f"Selected Book Value = "
        f"[{book_value}]"
    )

    page.screenshot(
        path="runtime/screenshots/"
        "otct_7968_tc002_after_book_enter.png"
    )

    # --------------------------------------------------
    # Source System values
    # --------------------------------------------------

    try:

        client_other = page.locator(
            "#puClientIdOther input"
        ).input_value()

        cm_mw = page.locator(
            "#puCmIdMw input"
        ).input_value()

        cm_other = page.locator(
            "#puCmIdOther input"
        ).input_value()

        log(
            f"Other Client ID = [{client_other}]"
        )

        log(
            f"MW CM ID = [{cm_mw}]"
        )

        log(
            f"Other CM ID = [{cm_other}]"
        )

    except Exception as e:

        log(
            f"Unable to read source system values: {e}"
        )

    page.screenshot(
        path="runtime/screenshots/"
        "otct_7968_tc002_source_system_values.png"
    )

    # --------------------------------------------------
    # MTM
    # --------------------------------------------------

    log("Clicking on MTM Adjustment dropdown")

    page.locator(
        PortfolioTransferLocators.MTM_FIELD
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting MTM Adjustment = No")

    page.locator(
        PortfolioTransferLocators.MTM_ADJ_OPTION
    ).click()

    page.wait_for_timeout(2000)

    page.screenshot(
        path="runtime/screenshots/"
        "otct_7968_tc002_after_mtm_selection.png"
    )

    # --------------------------------------------------
    # Create Portfolio Transfer
    # --------------------------------------------------

    log("Creating Portfolio Transfer")

    page.locator(
        PortfolioTransferLocators.CREATE_PORTFOLIO_TRANSFER
    ).click()

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/"
        "otct_7968_tc002_after_transfer.png"
    )

    # --------------------------------------------------
    # Result Validation
    # --------------------------------------------------

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

    if upload_status != "FAILURE":
        raise Exception(
            "Expected upload status "
            f"'FAILURE', got '{upload_status}'"
        )

    log(
        "TC002 PASSED - Upload status is "
        "FAILURE as expected"
    )

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()