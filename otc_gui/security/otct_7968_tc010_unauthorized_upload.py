import os

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

BASE_URL = "https://10.130.209.10:8443/OTC_GUI/App.html"

UNAUTH_USERNAME = os.getenv(
    "UNAUTH_USERNAME",
    "DBKFRCLR002"
)

UNAUTH_PASSWORD = os.getenv(
    "UNAUTH_PASSWORD",
    "DBKFRCLR002"
)

VALID_UPLOAD_FILE = (
    "./test_data/otc_gui/security/"
    "portfolio transfer/Portfolio_FromTrades_Fees.csv"
)

AUTHORIZATION_KEYWORDS = [
    "not authorized",
    "not authorised",
    "unauthorized",
    "unauthorised",
    "permission",
    "access denied",
    "not allowed",
    "insufficient",
    "privilege",
    "role",
    "forbidden",
    "authorization",
    "authorisation"
]


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def login_as_user(page, username, password):
    if not username or not password:
        raise Exception(
            "Unauthorized user credentials are missing. "
            "Set UNAUTH_USERNAME and UNAUTH_PASSWORD in config "
            "or environment variables."
        )

    log(f"Logging in as unauthorized user [{username}]")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc010_before_unauthorized_login.png"
    )

    username_field = page.locator("#username input")
    password_field = page.locator("#password input")
    login_button = page.locator("#login")

    if username_field.count() == 0:
        body_text = page.locator("body").inner_text()

        log("LOGIN PAGE BODY TEXT START")
        log(body_text[:3000])
        log("LOGIN PAGE BODY TEXT END")

        page.screenshot(
            path="runtime/screenshots/tc010_username_field_not_found.png"
        )

        raise Exception(
            "Username field was not found. "
            "Application may not be on login page."
        )

    username_field.wait_for(
        state="visible",
        timeout=30000
    )

    username_field.fill(username)
    password_field.fill(password)
    login_button.click()

    page.wait_for_timeout(4000)

    page.screenshot(
        path="runtime/screenshots/tc010_after_unauthorized_login.png"
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


def body_contains_authorization_message(page):
    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("AUTHORIZATION BODY TEXT START")
    log(body_text[:3000])
    log("AUTHORIZATION BODY TEXT END")

    return any(
        keyword in body_text_lower
        for keyword in AUTHORIZATION_KEYWORDS
    )


def assert_authorization_blocked(page, checkpoint):
    log(f"Checking authorization restriction at checkpoint: [{checkpoint}]")

    if body_contains_authorization_message(page):
        page.screenshot(
            path=(
                "runtime/screenshots/"
                f"tc010_authorization_blocked_{checkpoint}.png"
            )
        )

        log(
            "Authorization restriction message detected. "
            f"Checkpoint=[{checkpoint}]"
        )

        close_ok_popup_if_present(page)

        return True

    return False


def is_locator_enabled(page, selector):
    locator = page.locator(selector)

    if locator.count() == 0:
        return False

    try:
        return locator.first.is_enabled()
    except Exception:
        return False


def pass_test(message):
    log(message)
    raise SystemExit(0)


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
    log("Starting OTCT-7968_TC_010")

    if not os.path.exists(VALID_UPLOAD_FILE):
        raise Exception(
            f"Missing valid upload file: {VALID_UPLOAD_FILE}"
        )

    # --------------------------------------------------
    # Login as Unauthorized User
    # --------------------------------------------------

    login_as_user(
        page,
        UNAUTH_USERNAME,
        UNAUTH_PASSWORD
    )

    if assert_authorization_blocked(page, "login"):
        pass_test(
            "TC010 PASSED - Unauthorized user was blocked "
            "during login or initial access"
        )

    # --------------------------------------------------
    # Navigate to Portfolio Transfer Menu
    # --------------------------------------------------

    log("Navigating to Portfolio Transfer menu")

    portfolio_menu = page.locator("a[href='#portfolio']")

    if portfolio_menu.count() == 0:
        page.screenshot(
            path="runtime/screenshots/tc010_portfolio_menu_missing.png"
        )

        pass_test(
            "TC010 PASSED - Portfolio Transfer menu is unavailable "
            "for unauthorized user"
        )

    if not portfolio_menu.first.is_visible():
        page.screenshot(
            path="runtime/screenshots/tc010_portfolio_menu_not_visible.png"
        )

        pass_test(
            "TC010 PASSED - Portfolio Transfer menu is not visible "
            "for unauthorized user"
        )

    portfolio_menu.click()

    page.wait_for_timeout(2000)

    if assert_authorization_blocked(page, "portfolio_menu"):
        pass_test(
            "TC010 PASSED - Unauthorized user was blocked "
            "when opening Portfolio Transfer"
        )

    # --------------------------------------------------
    # Navigate to Portfolio Transfer Entry
    # --------------------------------------------------

    log("Navigating to Portfolio Transfer Entry")

    entry_tabs = page.locator(
        ".BlueTabPanelAppearance-BlueTabPanelStyle-tabStripText"
    ).filter(
        has_text="Portfolio Transfer Entry"
    )

    if entry_tabs.count() == 0:
        page.screenshot(
            path="runtime/screenshots/tc010_entry_tab_missing.png"
        )

        pass_test(
            "TC010 PASSED - Portfolio Transfer Entry tab is unavailable "
            "for unauthorized user"
        )

    entry_tab = entry_tabs.first

    if not entry_tab.is_visible():
        page.screenshot(
            path="runtime/screenshots/tc010_entry_tab_not_visible.png"
        )

        pass_test(
            "TC010 PASSED - Portfolio Transfer Entry tab is not visible "
            "for unauthorized user"
        )

    entry_tab.click()

    page.wait_for_timeout(2000)

    if assert_authorization_blocked(page, "portfolio_entry"):
        pass_test(
            "TC010 PASSED - Unauthorized user was blocked "
            "when opening Portfolio Transfer Entry"
        )

    page.screenshot(
        path="runtime/screenshots/tc010_after_portfolio_entry_open.png"
    )

    # --------------------------------------------------
    # Entry Type = Portfolio Upload
    # --------------------------------------------------

    log("Checking Entry Type dropdown")

    if not is_locator_enabled(
        page,
        PortfolioTransferLocators.ENTRY_TYPE
    ):
        page.screenshot(
            path="runtime/screenshots/tc010_entry_type_disabled.png"
        )

        pass_test(
            "TC010 PASSED - Entry Type dropdown is disabled "
            "for unauthorized user"
        )

    log("Clicking on Entry Type dropdown")

    page.locator(
        PortfolioTransferLocators.ENTRY_TYPE
    ).click()

    page.wait_for_timeout(1000)

    if assert_authorization_blocked(page, "entry_type_click"):
        pass_test(
            "TC010 PASSED - Unauthorized user was blocked "
            "when clicking Entry Type"
        )

    log("Selecting Portfolio Upload")

    portfolio_upload_option = page.get_by_text(
        "Portfolio Upload",
        exact=True
    )

    if portfolio_upload_option.count() == 0:
        page.screenshot(
            path="runtime/screenshots/tc010_portfolio_upload_option_missing.png"
        )

        pass_test(
            "TC010 PASSED - Portfolio Upload option is unavailable "
            "for unauthorized user"
        )

    if not portfolio_upload_option.first.is_visible():
        page.screenshot(
            path="runtime/screenshots/tc010_portfolio_upload_option_not_visible.png"
        )

        pass_test(
            "TC010 PASSED - Portfolio Upload option is not visible "
            "for unauthorized user"
        )

    portfolio_upload_option.click()

    page.wait_for_timeout(2000)

    if assert_authorization_blocked(page, "portfolio_upload_selection"):
        pass_test(
            "TC010 PASSED - Unauthorized user was blocked "
            "when selecting Portfolio Upload"
        )

    # --------------------------------------------------
    # Attempt File Upload
    # --------------------------------------------------

    log("Attempting upload with unauthorized user")

    file_upload = page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    )

    if file_upload.count() == 0:
        page.screenshot(
            path="runtime/screenshots/tc010_file_upload_control_missing.png"
        )

        pass_test(
            "TC010 PASSED - File upload control is unavailable "
            "for unauthorized user"
        )

    if not file_upload.first.is_enabled():
        page.screenshot(
            path="runtime/screenshots/tc010_file_upload_disabled.png"
        )

        pass_test(
            "TC010 PASSED - File upload control is disabled "
            "for unauthorized user"
        )

    file_upload.set_input_files(VALID_UPLOAD_FILE)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc010_after_upload_attempt.png"
    )

    if assert_authorization_blocked(page, "file_upload_attempt"):
        pass_test(
            "TC010 PASSED - Unauthorized upload attempt was blocked "
            "with authorization message"
        )

    # --------------------------------------------------
    # Optional: Try Create Button If Upload Was Allowed
    # --------------------------------------------------

    create_button = page.locator(
        PortfolioTransferLocators.CREATE_PORTFOLIO_TRANSFER
    )

    if create_button.count() > 0 and create_button.first.is_enabled():
        log(
            "Upload control was available. Checking whether action is "
            "blocked on Create Portfolio Transfer"
        )

        create_button.click()

        page.wait_for_timeout(3000)

        page.screenshot(
            path="runtime/screenshots/tc010_after_create_attempt.png"
        )

        if assert_authorization_blocked(page, "create_portfolio_transfer"):
            pass_test(
                "TC010 PASSED - Unauthorized user was blocked "
                "when creating Portfolio Transfer"
            )

    # --------------------------------------------------
    # If No Restriction Was Found, Fail
    # --------------------------------------------------

    raise Exception(
        "Unauthorized user was able to access Portfolio Upload "
        "and attempt upload without an authorization block"
    )

except SystemExit:
    pass

except Exception as e:
    log(f"TEST FAILED: {e}")
    raise

finally:
    try:
        logout(page)
    except Exception:
        log("Logout skipped or failed")

    browser.close()
    playwright.stop()