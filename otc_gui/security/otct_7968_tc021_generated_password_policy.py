import os
import re

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
    ""
)

PASSWORD_RESET_PASSWORD = os.getenv(
    "PASSWORD_RESET_PASSWORD",
    ""
)

RESET_TARGET_USER = os.getenv(
    "RESET_TARGET_USER",
    ""
)

MIN_PASSWORD_LENGTH = 8


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
        path="runtime/screenshots/tc030_before_login.png"
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
        path="runtime/screenshots/tc030_after_login.png"
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
            "Continuing with current page because Password Reset "
            "may be available on the current screen."
        )
        return False

    nav_item.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc030_after_user_management_navigation.png"
    )

    return True


def click_password_reset_button(page):
    log("Checking Password Reset button")

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

        log("BODY TEXT WHEN PASSWORD RESET BUTTON NOT FOUND START")
        log(body_text[:3000])
        log("BODY TEXT WHEN PASSWORD RESET BUTTON NOT FOUND END")

        page.screenshot(
            path="runtime/screenshots/tc030_password_reset_button_not_found.png"
        )

        raise Exception(
            "Password Reset button was not found for authorized user"
        )

    reset_button.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc030_password_reset_screen_opened.png"
    )


def enter_target_user_if_field_exists(page, target_user):
    if not target_user:
        log(
            "RESET_TARGET_USER was not provided. "
            "Skipping target-user entry."
        )
        return

    log(f"Trying to enter reset target user [{target_user}]")

    target_user_candidates = [
        "#userName input",
        "#username input",
        "#resetUser input",
        "#resetUsername input",
        "#userId input",
        "#userID input",
        "input[name='userName']",
        "input[name='username']",
        "input[name='userId']"
    ]

    target_field = find_visible_locator(
        page,
        target_user_candidates,
        "target user input"
    )

    if target_field is None:
        log(
            "Target user input was not found. "
            "Continuing because target user may already be selected "
            "or the reset popup may use a grid selection."
        )
        return

    target_field.click()
    target_field.press("Control+A")
    target_field.press("Delete")
    target_field.press_sequentially(target_user)
    target_field.press("Tab")

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc030_target_user_entered.png"
    )


def click_generate_password(page):
    log("Checking Generate Password button")

    generate_button_candidates = [
        "#generatePassword",
        "#generatePwd",
        "#passwordGenerate",
        "#generatePasswordButton",
        "button:has-text('Generate')",
        "div:has-text('Generate')",
        "span:has-text('Generate')",
        "a:has-text('Generate')",
        "button:has-text('Generate Password')",
        "div:has-text('Generate Password')",
        "span:has-text('Generate Password')",
        "a:has-text('Generate Password')"
    ]

    generate_button = find_visible_locator(
        page,
        generate_button_candidates,
        "Generate Password button"
    )

    if generate_button is None:
        body_text = page.locator("body").inner_text()

        log("BODY TEXT WHEN GENERATE PASSWORD BUTTON NOT FOUND START")
        log(body_text[:3000])
        log("BODY TEXT WHEN GENERATE PASSWORD BUTTON NOT FOUND END")

        page.screenshot(
            path="runtime/screenshots/tc030_generate_password_button_not_found.png"
        )

        raise Exception(
            "Generate Password button was not found"
        )

    generate_button.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc030_after_generate_password_click.png"
    )


def get_generated_password(page):
    log("Trying to read generated password")

    generated_password_candidates = [
        "#generatedPassword input",
        "#newPassword input",
        "#password input",
        "#resetPasswordNew input",
        "#resetGeneratedPassword input",
        "input[name='generatedPassword']",
        "input[name='newPassword']"
    ]

    for candidate in generated_password_candidates:
        locator = page.locator(candidate)

        if locator.count() == 0:
            continue

        for index in range(locator.count()):
            item = locator.nth(index)

            try:
                if item.is_visible():
                    value = item.input_value()

                    if value:
                        log(
                            "Generated password value read from "
                            f"candidate=[{candidate}]"
                        )
                        return value
            except Exception:
                pass

    # Fallback: detect visible password-like text in page body.
    # This is intentionally conservative and should be adjusted once
    # the exact generated-password locator is known.
    body_text = page.locator("body").inner_text()

    log("BODY TEXT WHILE SEARCHING GENERATED PASSWORD START")
    log(body_text[:3000])
    log("BODY TEXT WHILE SEARCHING GENERATED PASSWORD END")

    page.screenshot(
        path="runtime/screenshots/tc030_generated_password_not_readable.png"
    )

    raise Exception(
        "Generated password could not be read from known fields"
    )


def assert_generated_password_policy(password):
    log("Validating generated password policy compliance")

    checks = {
        "minimum_length": len(password) >= MIN_PASSWORD_LENGTH,
        "uppercase": re.search(r"[A-Z]", password) is not None,
        "lowercase": re.search(r"[a-z]", password) is not None,
        "digit": re.search(r"[0-9]", password) is not None,
        "special_character": re.search(r"[^A-Za-z0-9]", password) is not None
    }

    for check_name, passed in checks.items():
        log(f"Password policy check [{check_name}] = [{passed}]")

    failed_checks = [
        check_name
        for check_name, passed in checks.items()
        if not passed
    ]

    if failed_checks:
        raise Exception(
            "Generated password does not comply with expected policy. "
            f"Failed checks={failed_checks}"
        )

    log(
        "Generated password satisfies expected policy checks: "
        "minimum length, uppercase, lowercase, digit, and special character"
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
    log("Starting OTCT-7968_TC_030")

    # --------------------------------------------------
    # Login as PasswordResetUser
    # --------------------------------------------------

    login_as_user(
        page,
        PASSWORD_RESET_USERNAME,
        PASSWORD_RESET_PASSWORD
    )

    # --------------------------------------------------
    # Navigate to User Management
    # --------------------------------------------------

    click_user_management_if_available(page)

    # --------------------------------------------------
    # Open Password Reset
    # --------------------------------------------------

    click_password_reset_button(page)

    # --------------------------------------------------
    # Enter Target User If Required
    # --------------------------------------------------

    enter_target_user_if_field_exists(
        page,
        RESET_TARGET_USER
    )

    # --------------------------------------------------
    # Generate Password
    # --------------------------------------------------

    click_generate_password(page)

    # --------------------------------------------------
    # Read and Validate Generated Password
    # --------------------------------------------------

    generated_password = get_generated_password(page)

    # Do not log the actual password value.
    log(
        f"Generated password captured. "
        f"Length=[{len(generated_password)}]"
    )

    assert_generated_password_policy(
        generated_password
    )

    page.screenshot(
        path="runtime/screenshots/tc030_generated_password_policy_passed.png"
    )

    log(
        "OTCT-7968_TC_030 PASSED - Generated password complies "
        "with expected password policy"
    )

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()