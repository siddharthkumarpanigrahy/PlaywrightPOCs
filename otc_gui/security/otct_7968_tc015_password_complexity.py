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

BASE_URL = "https://10.130.209.10:8443/OTC_GUI/App.html"

CHANGE_PASSWORD_USERNAME = os.getenv(
    "CHANGE_PASSWORD_USERNAME",
    "DBKFRCLR002"
)

OLD_PASSWORD = os.getenv(
    "CHANGE_PASSWORD_OLD_PASSWORD",
    "Dummy-Old-Password-123"
)

# Intentionally weak password to violate complexity policy.
WEAK_PASSWORD = "abc"

EXPECTED_COMPLEXITY_KEYWORDS = [
    "password",
    "rule",
    "rules",
    "comply",
    "complexity",
    "minimum",
    "uppercase",
    "lowercase",
    "digit",
    "number",
    "special",
    "length",
    "must"
]


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

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


def assert_password_complexity_error(page):
    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("VALIDATION BODY TEXT START")
    log(body_text[:3000])
    log("VALIDATION BODY TEXT END")

    matched_keywords = [
        keyword
        for keyword in EXPECTED_COMPLEXITY_KEYWORDS
        if keyword in body_text_lower
    ]

    if not matched_keywords:
        page.screenshot(
            path="runtime/screenshots/tc029_password_complexity_error_not_found.png"
        )

        raise Exception(
            "Expected password complexity validation message was not found"
        )

    page.screenshot(
        path="runtime/screenshots/tc029_password_complexity_error_displayed.png"
    )

    log(
        "Password complexity validation message displayed. "
        f"Matched keywords={matched_keywords}"
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
    log("Starting OTCT-7968_TC_029")

    # --------------------------------------------------
    # Open Login Page
    # --------------------------------------------------

    log("Opening OTC GUI login page")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc029_login_page.png"
    )

    # --------------------------------------------------
    # Open Change Password Screen
    # --------------------------------------------------

    log("Opening Change Password screen")

    change_password_button = page.locator("#changePassword")

    change_password_button.wait_for(
        state="visible",
        timeout=30000
    )

    change_password_button.click()

    page.wait_for_timeout(2000)

    page.screenshot(
        path="runtime/screenshots/tc029_change_password_screen.png"
    )

    # --------------------------------------------------
    # Fill Change Password Form With Weak Password
    # --------------------------------------------------

    log("Entering weak password values")

    username_field = page.locator(
        "#changePasswordUser input"
    )

    old_password_field = page.locator(
        "#changePasswordOld input"
    )

    new_password_field = page.locator(
        "#changePasswordNew input"
    )

    repeat_password_field = page.locator(
        "#changePasswordRepeat input"
    )

    send_button = page.locator("#changePasswordSend")

    username_field.wait_for(
        state="visible",
        timeout=30000
    )

    username_field.fill(CHANGE_PASSWORD_USERNAME)
    old_password_field.fill(OLD_PASSWORD)
    new_password_field.fill(WEAK_PASSWORD)
    repeat_password_field.fill(WEAK_PASSWORD)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc029_weak_password_values_entered.png"
    )

    # --------------------------------------------------
    # Submit
    # --------------------------------------------------

    log("Submitting Change Password form")

    send_button.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc029_after_submit.png"
    )

    # --------------------------------------------------
    # Validate Complexity Error
    # --------------------------------------------------

    assert_password_complexity_error(page)

    log(
        "OTCT-7968_TC_029 PASSED - Password complexity "
        "validation was displayed for weak password"
    )

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()