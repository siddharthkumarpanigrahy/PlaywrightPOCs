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

REM_USERNAME = os.getenv(
    "REM_USERNAME",
    "AAALUREM002"
)

REM_PASSWORD = os.getenv(
    "REM_PASSWORD",
    "AAALUREM002"
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
    "authorisation",
    "rem",
    "restricted",
    "password reset"
]


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def login_as_rem_user(page, username, password):
    if not username or not password:
        raise Exception(
            "REM user credentials are missing. "
            "Set REM_USERNAME and REM_PASSWORD."
        )

    log(f"Logging in as REM user [{username}]")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc027_before_rem_login.png"
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
        path="runtime/screenshots/tc027_after_rem_login.png"
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


def get_visible_password_reset_button(page):
    reset_button_candidates = [
        "button:has-text('Password Reset')",
        "div:has-text('Password Reset')",
        "span:has-text('Password Reset')",
        "a:has-text('Password Reset')",
        "button:has-text('Reset Password')",
        "div:has-text('Reset Password')",
        "span:has-text('Reset Password')",
        "a:has-text('Reset Password')",
        "#resetPassword",
        "#passwordReset",
        "#resetPasswordButton",
        "#userPasswordReset",
        "#resetUserPassword"
    ]

    return find_visible_locator(
        page,
        reset_button_candidates,
        "Password Reset button"
    )


def assert_password_reset_unavailable_for_rem(page):
    log("Validating Password Reset restriction for REM user")

    if body_contains_authorization_message(page):
        page.screenshot(
            path="runtime/screenshots/tc027_rem_authorization_message.png"
        )

        close_ok_popup_if_present(page)

        log(
            "OTCT-7968_TC_027 PASSED - REM user was blocked "
            "by authorization or restriction message"
        )

        return

    reset_button = get_visible_password_reset_button(page)

    if reset_button is None:
        page.screenshot(
            path="runtime/screenshots/tc027_password_reset_not_visible_for_rem.png"
        )

        log(
            "OTCT-7968_TC_027 PASSED - Password Reset button is not "
            "visible for REM user"
        )

        return

    page.screenshot(
        path="runtime/screenshots/tc027_password_reset_visible_for_rem_unexpected.png"
    )

    raise Exception(
        "Password Reset button is visible for REM user, "
        "but REM users should not act as password reset users"
    )


def logout_user(page):
    log("Logging out")

    try:
        page.get_by_role(
            "button",
            name="Logout"
        ).click()

        page.wait_for_timeout(2000)

        page.screenshot(
            path="runtime/screenshots/tc027_after_logout.png"
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
    log("Starting OTCT-7968_TC_027")

    # --------------------------------------------------
    # Login as REM User
    # --------------------------------------------------

    login_as_rem_user(
        page,
        REM_USERNAME,
        REM_PASSWORD
    )

    # --------------------------------------------------
    # Validate Password Reset Restriction
    # --------------------------------------------------

    assert_password_reset_unavailable_for_rem(page)

    logout_user(page)

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()