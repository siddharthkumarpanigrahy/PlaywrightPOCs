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

PASSWORD_RESET_USERNAME = os.getenv(
    "PASSWORD_RESET_USERNAME",
    "CBKFRCLR001"
)

PASSWORD_RESET_PASSWORD = os.getenv(
    "PASSWORD_RESET_PASSWORD",
    "CBKFRCLR001"
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def login_as_user(page, username, password):
    if not username or not password:
        raise Exception(
            "PasswordResetUser credentials are missing. "
            "Set PASSWORD_RESET_USERNAME and PASSWORD_RESET_PASSWORD."
        )

    log(f"Logging in as PasswordResetUser [{username}]")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc023_before_login.png"
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
        path="runtime/screenshots/tc023_after_login.png"
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
            "Continuing with current page because Reset Password may be "
            "available on the main page."
        )
        return False

    nav_item.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc023_after_user_management_navigation.png"
    )

    return True


def assert_reset_password_button_visible(page):
    log("Checking Password Reset button visibility")

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

    reset_button = find_visible_locator(
        page,
        reset_button_candidates,
        "Password Reset button"
    )

    if reset_button is None:
        body_text = page.locator("body").inner_text()

        log("BODY TEXT WHEN RESET BUTTON NOT FOUND START")
        log(body_text[:3000])
        log("BODY TEXT WHEN RESET BUTTON NOT FOUND END")

        page.screenshot(
            path="runtime/screenshots/tc023_reset_password_button_not_found.png"
        )

        raise Exception(
            "Password Reset button was not visible for authorized "
            "PasswordResetUser"
        )

    page.screenshot(
        path="runtime/screenshots/tc023_reset_password_button_visible.png"
    )

    log(
        "OTCT-7968_TC_023 PASSED - Password Reset button is visible "
        "for user authorized with PasswordResetUser role"
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
    log("Starting OTCT-7968_TC_023")

    # --------------------------------------------------
    # Login as PasswordResetUser
    # --------------------------------------------------

    login_as_user(
        page,
        PASSWORD_RESET_USERNAME,
        PASSWORD_RESET_PASSWORD
    )

    # --------------------------------------------------
    # Navigate to User Management if available
    # --------------------------------------------------

    click_user_management_if_available(page)

    # --------------------------------------------------
    # Validate Password Reset Button
    # --------------------------------------------------

    assert_reset_password_button_visible(page)

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()
