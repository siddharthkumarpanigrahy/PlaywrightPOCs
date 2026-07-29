import os
from abc import ABC, abstractmethod
from playwright.sync_api import Page as PlaywrightPage

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

    # Entry Type dropdown
    log("Clicking on Entry Type dropdown")
    page.locator(
        PortfolioTransferLocators.ENTRY_TYPE
    ).click()

    page.wait_for_timeout(1000)

    # Portfolio Upload
    log("Clicking on Portfolio Upload")
    page.get_by_text(
        "Portfolio Upload"
    ).click()

    page.wait_for_timeout(2000)

    # trailing space file path
    log("Preparing to upload file with trailing space in filename")
    TrailingSpace_filename_file = (
        "./test_data/otc_gui/security/portfolio transfer/TrailingSpace .csv"
    )

    # Uplload file with long filename
    log("Uploading file with trailing space in filename")
    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(TrailingSpace_filename_file)

    # Transfer Type
    log("Clicking on Transfer Type dropdown")
    page.locator(
        PortfolioTransferLocators.TRANSFER_TYPE
    ).click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/otct_7968_tc002_transfer_type_dropdown.png"
    )

    # Account Transfer Option
    log("Selecting Account Transfer option")
    page.locator(
        PortfolioTransferLocators.ACCOUNT_TRANSFER_OPTION
    ).filter(
        has_text="Account Transfer"
    ).first.click()

    # Book
    log("Clicking on Book dropdown")
    page.locator(
        PortfolioTransferLocators.BOOK
    ).click()

    # Book Option
    log("Selecting Book option 'CBKFR_A1'")
    page.locator(
        PortfolioTransferLocators.BOOK_OPTION
    ).filter(
        has_text="CBKFR_A1"
    ).first.click()

    # MTM
    log("Clicking on MTM Adj dropdown")
    page.locator(
        PortfolioTransferLocators.MTM_ADJ
    ).click()

    # MTM Option
    log("Selecting MTM Adj option 'No'")
    page.get_by_text(
        "No"
    ).click()

    # Create Portfolio Transfer
    log("Creating Portfolio Transfer")
    page.locator(
        PortfolioTransferLocators.CREATE_PORTFOLIO_TRANSFER
    ).click()

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/otct_7968_tc002_after_upload.png"
    )

    log("File uploaded successfully")

    logout(page)

except Exception as e:
    log(f"TEST FAILED: {e}")

finally:
    browser.close()
    playwright.stop()