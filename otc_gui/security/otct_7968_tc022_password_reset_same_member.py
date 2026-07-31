
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

RESET_NEW_PASSWORD = os.getenv(
    "RESET_NEW_PASSWORD",
    "ValidTest-123!"
)

SUCCESS_KEYWORDS = [
    "success",
    "successfully",
    "password reset",
    "password has been reset",
    "reset completed",
    "completed successfully"
]

AUTHORIZATION_BLOCK_KEYWORDS = [
    "not authorized",
    "not authorised",
    "unauthorized",
    "unauthorised",
    "access denied",
    "permission",
    "not allowed",
    "forbidden",
    "different member",
    "member id"
]


# --------------------------------------------------
# Generic Helpers
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
        path="runtime/screenshots/tc025_before_login.png"
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
        path="runtime/screenshots/tc025_after_login.png"
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


def close_ok_popup_if_present(page):
    ok_candidates = [
        "button:has-text('OK')",
        "button:has-text('Ok')",
        "div:has-text('OK')",
        "div:has-text('Ok')",
        "span:has-text('OK')",
        "span:has-text('Ok')"
    ]

    ok_button = find_visible_locator(
        page,
        ok_candidates,
        "OK button"
    )

    if ok_button is not None:
        ok_button.click()
        page.wait_for_timeout(1000)
        log("Popup closed using OK")
        return True

    return False


def click_visible_text_if_present(page, texts, description):
    for text in texts:
        items = page.get_by_text(
            text,
            exact=True
        )

        if items.count() == 0:
            continue

        for index in range(items.count()):
            item = items.nth(index)

            try:
                if item.is_visible():
                    item.click()
                    page.wait_for_timeout(1000)
                    log(f"Clicked {description}: [{text}]")
                    return True
            except Exception:
                pass

    return False


def confirm_if_present(page, screenshot_prefix):
    confirm_texts = [
        "Confirm",
        "Yes",
        "OK",
        "Ok"
    ]

    body_text = page.locator("body").inner_text()

    if (
        "confirm" not in body_text.lower()
        and "are you sure" not in body_text.lower()
        and "reset" not in body_text.lower()
    ):
        log("No confirmation popup detected")
        return False

    page.screenshot(
        path=f"runtime/screenshots/{screenshot_prefix}_confirmation_popup.png"
    )

    clicked = click_visible_text_if_present(
        page,
        confirm_texts,
        "confirmation button"
    )

    if clicked:
        log("Confirmation popup handled")
        return True

    log("Confirmation text may be present, but no confirmation button was clicked")
    return False


def body_contains_any(page, keywords):
    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    return any(
        keyword.lower() in body_text_lower
        for keyword in keywords
    )


def log_body_text(page, label):
    body_text = page.locator("body").inner_text()

    log(f"{label} BODY TEXT START")
    log(body_text[:4000])
    log(f"{label} BODY TEXT END")


# --------------------------------------------------
# Navigation Helpers
# --------------------------------------------------

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
            "Continuing because Password Reset may be available "
            "on the current screen."
        )
        return False

    nav_item.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc025_after_user_management_navigation.png"
    )

    return True


def open_password_reset_screen(page):
    log("Opening Password Reset screen")

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
        log_body_text(
            page,
            "PASSWORD RESET BUTTON NOT FOUND"
        )

        page.screenshot(
            path="runtime/screenshots/tc025_password_reset_button_not_found.png"
        )

        raise Exception(
            "Password Reset button was not found for authorized user"
        )

    reset_button.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc025_password_reset_screen_opened.png"
    )


# --------------------------------------------------
# Password Reset Form Helpers
# --------------------------------------------------

def enter_target_user(page, target_user):
    if not target_user:
        raise Exception(
            "RESET_TARGET_USER is missing. "
            "Set RESET_TARGET_USER to a same-Member-ID test user."
        )

    log(f"Entering reset target user [{target_user}]")

    target_user_candidates = [
        "#userName input",
        "#username input",
        "#resetUser input",
        "#resetUsername input",
        "#userId input",
        "#userID input",
        "#targetUser input",
        "#targetUsername input",
        "input[name='userName']",
        "input[name='username']",
        "input[name='userId']",
        "input[name='targetUser']"
    ]

    target_field = find_visible_locator(
        page,
        target_user_candidates,
        "target user input"
    )

    if target_field is None:
        log_body_text(
            page,
            "TARGET USER FIELD NOT FOUND"
        )

        page.screenshot(
            path="runtime/screenshots/tc025_target_user_field_not_found.png"
        )

        raise Exception(
            "Target user input was not found on Password Reset screen"
        )

    target_field.click()
    target_field.press("Control+A")
    target_field.press("Delete")
    target_field.press_sequentially(target_user)
    target_field.press("Tab")

    page.wait_for_timeout(1500)

    page.screenshot(
        path="runtime/screenshots/tc025_target_user_entered.png"
    )


def fill_manual_password_if_fields_exist(page, new_password):
    log("Checking for manual Password and Confirm Password fields")

    password_candidates = [
        "#newPassword input",
        "#password input",
        "#resetPasswordNew input",
        "#generatedPassword input",
        "#changePasswordNew input",
        "input[name='newPassword']",
        "input[name='password']"
    ]

    confirm_candidates = [
        "#confirmPassword input",
        "#repeatPassword input",
        "#resetPasswordRepeat input",
        "#changePasswordRepeat input",
        "input[name='confirmPassword']",
        "input[name='repeatPassword']"
    ]

    password_field = find_visible_locator(
        page,
        password_candidates,
        "new password input"
    )

    confirm_field = find_visible_locator(
        page,
        confirm_candidates,
        "confirm password input"
    )

    if password_field is None or confirm_field is None:
        log(
            "Manual password fields not found. "
            "The screen may use generated password flow."
        )
        return False

    log("Entering new password and confirm password")

    password_field.click()
    password_field.press("Control+A")
    password_field.press("Delete")
    password_field.press_sequentially(new_password)

    confirm_field.click()
    confirm_field.press("Control+A")
    confirm_field.press("Delete")
    confirm_field.press_sequentially(new_password)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc025_password_fields_entered.png"
    )

    return True


def click_generate_password_if_available(page):
    log("Checking for Generate Password button")

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
        log("Generate Password button not found")
        return False

    generate_button.click()

    page.wait_for_timeout(2000)

    page.screenshot(
        path="runtime/screenshots/tc025_after_generate_password_click.png"
    )

    log("Generate Password button clicked")
    return True


def submit_password_reset(page):
    log("Submitting password reset request")

    submit_candidates = [
        "#resetPasswordSubmit",
        "#submitPasswordReset",
        "#passwordResetSubmit",
        "#resetPasswordSend",
        "#sendPasswordReset",
        "button:has-text('Submit')",
        "button:has-text('Send')",
        "button:has-text('Save')",
        "button:has-text('Reset')",
        "div:has-text('Submit')",
        "div:has-text('Send')",
        "div:has-text('Save')",
        "div:has-text('Reset')",
        "span:has-text('Submit')",
        "span:has-text('Send')",
        "span:has-text('Save')",
        "span:has-text('Reset')"
    ]

    submit_button = find_visible_locator(
        page,
        submit_candidates,
        "password reset submit button"
    )

    if submit_button is None:
        log_body_text(
            page,
            "SUBMIT BUTTON NOT FOUND"
        )

        page.screenshot(
            path="runtime/screenshots/tc025_submit_button_not_found.png"
        )

        raise Exception(
            "Password reset submit button was not found"
        )

    submit_button.click()

    page.wait_for_timeout(2000)

    confirm_if_present(
        page,
        "tc025"
    )

    page.wait_for_timeout(4000)

    page.screenshot(
        path="runtime/screenshots/tc025_after_password_reset_submit.png"
    )


def assert_password_reset_success(page):
    log("Validating same-member password reset success")

    if body_contains_any(
        page,
        AUTHORIZATION_BLOCK_KEYWORDS
    ):
        log_body_text(
            page,
            "AUTHORIZATION BLOCK DETECTED"
        )

        page.screenshot(
            path="runtime/screenshots/tc025_authorization_block_detected.png"
        )

        raise Exception(
            "Password reset was blocked, but TC025 expects success "
            "for same Member ID target user"
        )

    if not body_contains_any(
        page,
        SUCCESS_KEYWORDS
    ):
        log_body_text(
            page,
            "SUCCESS MESSAGE NOT FOUND"
        )

        page.screenshot(
            path="runtime/screenshots/tc025_success_message_not_found.png"
        )

        raise Exception(
            "Expected password reset success message was not found"
        )

    page.screenshot(
        path="runtime/screenshots/tc025_password_reset_success.png"
    )

    log(
        "OTCT-7968_TC_025 PASSED - Authorized PasswordResetUser "
        "successfully reset password for same Member ID user"
    )

    close_ok_popup_if_present(page)


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
    log("Starting OTCT-7968_TC_025")

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
    # Open Password Reset Screen
    # --------------------------------------------------

    open_password_reset_screen(page)

    # --------------------------------------------------
    # Enter Same-Member Target User
    # --------------------------------------------------

    enter_target_user(
        page,
        RESET_TARGET_USER
    )

    # --------------------------------------------------
    # Either generate password or fill manual fields
    # --------------------------------------------------

    generated = click_generate_password_if_available(page)

    if not generated:
        fill_manual_password_if_fields_exist(
            page,
            RESET_NEW_PASSWORD
        )

    # --------------------------------------------------
    # Submit Password Reset
    # --------------------------------------------------

    submit_password_reset(page)

    # --------------------------------------------------
    # Validate Success
    # --------------------------------------------------

    assert_password_reset_success(page)

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()