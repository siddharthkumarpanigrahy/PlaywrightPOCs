from playwright.sync_api import Page
from common.logger import log

from common.config import (
    OTC_GUI_URL,
    USERNAME,
    PASSWORD
)

from locators.otc_gui.login_locators import (
    USERNAME_TEXTBOX,
    PASSWORD_TEXTBOX,
    LOGIN_BUTTON
)


def login(page: Page):

    log("Opening OTC GUI...")

    page.goto(
        OTC_GUI_URL,
        wait_until="domcontentloaded"
    )
    log(f"Opening URL: {OTC_GUI_URL}")
    log(f"Page Loaded: {page.title()}")

    page.locator(
        USERNAME_TEXTBOX
    ).fill(USERNAME)

    page.locator(
        PASSWORD_TEXTBOX
    ).fill(PASSWORD)

    log("Credentials entered")

    page.locator(
        LOGIN_BUTTON
    ).click()

    log("Login button clicked!")