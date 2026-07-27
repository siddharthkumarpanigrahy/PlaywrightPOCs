from playwright.sync_api import Page
from common.logger import log

from locators.otc_gui.logout_locators import (
    LOGOUT_BUTTON
)


def logout(page: Page):

    log("Logging out...")

    page.locator(
        LOGOUT_BUTTON
    ).click()

    log("Logout button clicked!")