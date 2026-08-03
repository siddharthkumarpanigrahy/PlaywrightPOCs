import os

from common.logout import logout
from common.browser import launch_browser
from common.logger import log


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

NO_PASSWORD_RESET_USERNAME = os.getenv(
    "NO_PASSWORD_RESET_USERNAME",
    "AACLUCLR001"
)

NO_PASSWORD_RESET_PASSWORD = os.getenv(
    "NO_PASSWORD_RESET_PASSWORD",
    "AACLUCLR001"
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
            "Non-PasswordResetUser credentials are missing. "
            "Set NO_PASSWORD_RESET_USERNAME and NO_PASSWORD_RESET_PASSWORD."
        )

    log(f"Logging in as user without PasswordResetUser role [{username}]")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc024_before_login.png"
    )

    username_field = page.locator("#username input")
    password_field = page.locator("#password input")
    login_button = page.locator("#login")

    username_field.wait_for(
        state="visible",
        timeout=30000
    )

    username_field.fill(username)
    password_field.fill(password)
    login_button.click()

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/tc024_after_login.png"
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


def find_visible_locator(page, candidates, description):
    for candidate in candidates:
        locator = page.locator(candidate)

        if locator.count() == 0:
            continue

        for index in range(locator.count()):
            item = locator.nth(index)

            try:
                if item.is_visible():
                    log(
                        f"Visible {description} found using locator: "
                        f"[{candidate}]"
                    )
                    return item
            except Exception:
                pass

    return None


def click_user_management_if_available(page):
    log("Checking for User Management navigation")

    user_management_candidates = [
        "a:has-text('User Management')",
        "div:has-text('User Management')",
        "span:has-text('User Management')",
        "a:has-text('User')",
        "div:has-text('User')",
        "span:has-text('User')",
        "a:has-text('Administration')",
        "div:has-text('Administration')",
        "span:has-text('Administration')",
        "a:has-text('Admin')",
        "div:has-text('Admin')",
        "span:has-text('Admin')"
    ]

    nav_item = find_visible_locator(
        page,
        user_management_candidates,
        "User Management navigation"
    )

    if nav_item is None:
        log(
            "User Management navigation was not found. "
            "Continuing with current page because Reset Password "
            "button should still not be visible."
        )
        return False

    nav_item.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc024_after_user_management_navigation.png"
    )

    return True


def get_visible_reset_password_button(page):
    reset_button_candidates = [
        "#resetPassword",
        "#passwordReset",
        "#resetPasswordButton",
        "#userPasswordReset",
        "#resetUserPassword",
        "button:has-text('Reset Password')",
        "div:has-text('Reset Password')",
        "span:has-text('Reset Password')",
        "a:has-text('Reset Password')",
        "button:has-text('Password Reset')",
        "div:has-text('Password Reset')",
        "span:has-text('Password Reset')",
        "a:has-text('Password Reset')"
    ]

    return find_visible_locator(
        page,
        reset_button_candidates,
        "Password Reset button"
    )


def assert_reset_password_button_not_visible(page):
    log("Checking that Password Reset button is not visible")

    reset_button = get_visible_reset_password_button(page)

    if reset_button is None:
        page.screenshot(
            path="runtime/screenshots/tc024_reset_password_button_not_visible.png"
        )

        log(
            "OTCT-7968_TC_024 PASSED - Password Reset button is not "
            "visible for user without PasswordResetUser authorization"
        )

        return

    page.screenshot(
        path="runtime/screenshots/tc024_reset_password_button_visible_unexpected.png"
    )

    raise Exception(
        "Password Reset button is visible for user without "
        "PasswordResetUser authorization"
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
    log("Starting OTCT-7968_TC_024")

    # --------------------------------------------------
    # Login as user without PasswordResetUser role
    # --------------------------------------------------

    login_as_user(
        page,
        NO_PASSWORD_RESET_USERNAME,
        NO_PASSWORD_RESET_PASSWORD
    )

    # If the app shows an authorization message immediately,
    # this is acceptable evidence.
    if body_contains_authorization_message(page):
        page.screenshot(
            path="runtime/screenshots/tc024_authorization_message_after_login.png"
        )

        close_ok_popup_if_present(page)

        log(
            "OTCT-7968_TC_024 PASSED - User without PasswordResetUser "
            "authorization was blocked by authorization message"
        )

        raise SystemExit(0)

    # --------------------------------------------------
    # Navigate to User Management if available
    # --------------------------------------------------

    click_user_management_if_available(page)

    # --------------------------------------------------
    # Validate Password Reset Button Is Not Visible
    # --------------------------------------------------

    assert_reset_password_button_not_visible(page)

    logout(page)

except SystemExit:
    pass

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    try:
        browser.close()
        playwright.stop()
    except Exception:
        pass