
import os

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

RESET_TARGET_USER_DIFFERENT_MEMBER = os.getenv(
    "RESET_TARGET_USER_DIFFERENT_MEMBER",
    "DBKFRCLR001"
)

EXPECTED_ERROR_MESSAGE = "The provided User ID does not"


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def fill_login(page, username, password):
    log(f"Logging in as PasswordResetUser [{username}]")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc026_before_login.png"
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
        path="runtime/screenshots/tc026_after_login.png"
    )


def open_password_reset(page):
    log("Opening Password Reset screen")

    page.get_by_role(
        "button",
        name="Password Reset"
    ).click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc026_password_reset_screen_opened.png"
    )


def enter_different_member_user(page, target_user):
    log(
        f"Entering different-member target user "
        f"[{target_user}]"
    )

    target_user_field = page.locator("#x-auto-67-input")

    target_user_field.wait_for(
        state="visible",
        timeout=30000
    )

    target_user_field.click()
    target_user_field.fill(target_user)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc026_target_user_entered.png"
    )


def generate_and_confirm_password(page):
    log("Generating password")

    page.get_by_role(
        "button",
        name="Generate Password"
    ).click()

    page.wait_for_timeout(2000)

    generated_password_field = page.locator("#x-auto-69-input")
    confirm_password_field = page.locator("#x-auto-70-input")

    generated_password_field.wait_for(
        state="visible",
        timeout=30000
    )

    generated_password = generated_password_field.input_value()

    if not generated_password:
        page.screenshot(
            path="runtime/screenshots/tc026_generated_password_empty.png"
        )

        raise Exception(
            "Generated password field is empty"
        )

    log(
        "Generated password captured. "
        f"Length=[{len(generated_password)}]"
    )

    confirm_password_field.click()
    confirm_password_field.fill(generated_password)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc026_generated_password_confirmed.png"
    )


def submit_password_reset(page):
    log("Submitting password reset request")

    page.get_by_role(
        "button",
        name="Submit"
    ).click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc026_after_submit.png"
    )


def validate_different_member_error(page):
    log(
        f"Validating expected error message "
        f"[{EXPECTED_ERROR_MESSAGE}]"
    )

    error_message = page.get_by_text(
        EXPECTED_ERROR_MESSAGE,
        exact=False
    )

    error_message.wait_for(
        state="visible",
        timeout=30000
    )

    page.screenshot(
        path="runtime/screenshots/tc026_different_member_error_displayed.png"
    )

    log(
        "Expected different-member authorization error "
        "message displayed"
    )

    page.get_by_text(
        "OK",
        exact=True
    ).click()

    page.wait_for_timeout(1000)


def logout_user(page):
    log("Logging out")

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
        path="runtime/screenshots/tc026_after_logout.png"
    )

    log("Logout completed")


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
    # Login
    # --------------------------------------------------

    fill_login(
        page,
        PASSWORD_RESET_USERNAME,
        PASSWORD_RESET_PASSWORD
    )

    # --------------------------------------------------
    # Password Reset
    # --------------------------------------------------

    open_password_reset(page)

    enter_different_member_user(
        page,
        RESET_TARGET_USER_DIFFERENT_MEMBER
    )

    generate_and_confirm_password(page)

    submit_password_reset(page)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    validate_different_member_error(page)

    log(
        "OTCT-7968_TC_023 PASSED - Password reset for "
        "different Member ID user was blocked with expected "
        "authorization validation"
    )

    logout_user(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()