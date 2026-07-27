from playwright.sync_api import Page

from locators.otc_gui.logout_locators import (
    LOGOUT_BUTTON
)


def logout(page: Page):

    print("Logging out...")

    page.locator(
        LOGOUT_BUTTON
    ).click()

    print("Logout button clicked!")