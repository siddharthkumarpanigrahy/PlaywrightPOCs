import os
import re

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

BASE_URL = "https://10.130.209.10:8443/OTC_GUI/App.html#login"

PASSWORD_RESET_USERNAME = os.getenv(
    "PASSWORD_RESET_USERNAME",
    "CBKFRCLR001"
)

PASSWORD_RESET_PASSWORD = os.getenv(
    "PASSWORD_RESET_PASSWORD",
    "CBKFRCLR001"
)

RESET_TARGET_USER = os.getenv(
    "RESET_TARGET_USER",
    "DBKFRCLR001"
)

MIN_PASSWORD_LENGTH = int(
    os.getenv(
        "MIN_PASSWORD_LENGTH",
        "8"
    )
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def login_as_password_reset_user(page, username, password):
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

    username_field = page.locator("#x-auto-11-input")
    password_field = page.locator("#x-auto-12-input")

    username_field.wait_for(
        state="visible",
        timeout=30000
    )

    username_field.click()
    username_field.fill(username)

    password_field.click()
    password_field.fill(password)

    page.get_by_role(
        "button",
        name="Login"
    ).click()

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/tc030_after_login.png"
    )


def open_password_reset_screen(page):
    log("Opening Password Reset screen")

    page.get_by_role(
        "button",
        name="Password Reset"
    ).click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc030_password_reset_screen_opened.png"
    )


def enter_target_user(page, target_user):
    if not target_user:
        raise Exception(
            "RESET_TARGET_USER is missing. "
            "Set RESET_TARGET_USER for generated password validation."
        )

    log(f"Entering reset target user [{target_user}]")

    target_user_field = page.locator("#x-auto-67-input")

    target_user_field.wait_for(
        state="visible",
        timeout=30000
    )

    target_user_field.click()
    target_user_field.fill(target_user)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc030_target_user_entered.png"
    )


def generate_password(page):
    log("Generating password")

    page.get_by_role(
        "button",
        name="Generate Password"
    ).click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc030_after_generate_password_click.png"
    )


def read_generated_password(page):
    log("Reading generated password from generated password field")

    generated_password_field = page.locator("#x-auto-69-input")

    generated_password_field.wait_for(
        state="visible",
        timeout=30000
    )

    generated_password = generated_password_field.input_value()

    if not generated_password:
        page.screenshot(
            path="runtime/screenshots/tc030_generated_password_empty.png"
        )

        raise Exception(
            "Generated password field is empty"
        )

    log(
        "Generated password captured successfully. "
        f"Length=[{len(generated_password)}]"
    )

    return generated_password


def populate_confirm_password(page, generated_password):
    log("Populating Confirm Password field with generated password")

    confirm_password_field = page.locator("#x-auto-70-input")

    confirm_password_field.wait_for(
        state="visible",
        timeout=30000
    )

    confirm_password_field.click()
    confirm_password_field.fill(generated_password)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc030_generated_password_confirmed.png"
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


def logout_user(page):
    log("Logging out")

    try:
        close_button = page.locator(
            ".IconButtonDefaultAppearance-IconButtonStyle-button"
        )

        if close_button.count() > 0:
            try:
                if close_button.first.is_visible():
                    close_button.first.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass

        page.get_by_role(
            "button",
            name="Logout"
        ).click()

        page.wait_for_timeout(2000)

        page.screenshot(
            path="runtime/screenshots/tc030_after_logout.png"
        )

        log("Logout completed")

    except Exception:
        log("Logout button not found or logout skipped")


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
    # Login
    # --------------------------------------------------

    login_as_password_reset_user(
        page,
        PASSWORD_RESET_USERNAME,
        PASSWORD_RESET_PASSWORD
    )

    # --------------------------------------------------
    # Open Password Reset
    # --------------------------------------------------

    open_password_reset_screen(page)

    # --------------------------------------------------
    # Enter Target User
    # --------------------------------------------------

    enter_target_user(
        page,
        RESET_TARGET_USER
    )

    # --------------------------------------------------
    # Generate Password
    # --------------------------------------------------

    generate_password(page)

    # --------------------------------------------------
    # Read Generated Password
    # --------------------------------------------------

    generated_password = read_generated_password(page)

    # --------------------------------------------------
    # Confirm Password Field
    # --------------------------------------------------

    populate_confirm_password(
        page,
        generated_password
    )

    # --------------------------------------------------
    # Validate Password Policy
    # --------------------------------------------------

    assert_generated_password_policy(
        generated_password
    )

    page.screenshot(
        path="runtime/screenshots/tc030_generated_password_policy_passed.png"
    )

    log(
        "OTCT-7968_TC_030 PASSED - Generated password complies "
        "with configured password policy"
    )

    logout_user(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()