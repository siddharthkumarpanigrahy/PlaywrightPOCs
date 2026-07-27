from playwright.sync_api import Page

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

    print("Opening OTC GUI...")

    page.goto(
        OTC_GUI_URL,
        wait_until="domcontentloaded"
    )

    print(f"Page Loaded: {page.title()}")

    page.locator(
        USERNAME_TEXTBOX
    ).fill(USERNAME)

    page.locator(
        PASSWORD_TEXTBOX
    ).fill(PASSWORD)

    print("Credentials entered")

    page.locator(
        LOGIN_BUTTON
    ).click()

    print("Login button clicked!")