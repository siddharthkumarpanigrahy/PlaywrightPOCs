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

TEST_PASSWORD = "MaskTest-123"


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
    log("Starting OTCT-7968_TC_031")

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
        path="runtime/screenshots/tc031_login_page.png"
    )

    # --------------------------------------------------
    # Open Change Password / Password Reset Screen
    # --------------------------------------------------

    log("Opening password change/reset screen")

    change_password_button = page.locator("#changePassword")

    change_password_button.wait_for(
        state="visible",
        timeout=30000
    )

    change_password_button.click()

    page.wait_for_timeout(2000)

    page.screenshot(
        path="runtime/screenshots/tc031_password_screen_opened.png"
    )

    # --------------------------------------------------
    # Locate Password Fields
    # --------------------------------------------------

    new_password_field = page.locator(
        "#changePasswordNew input"
    )

    confirm_password_field = page.locator(
        "#changePasswordRepeat input"
    )

    new_password_field.wait_for(
        state="visible",
        timeout=30000
    )

    confirm_password_field.wait_for(
        state="visible",
        timeout=30000
    )

    # --------------------------------------------------
    # Enter Password Values
    # --------------------------------------------------

    log("Entering values in Password and Confirm Password fields")

    new_password_field.fill(TEST_PASSWORD)
    confirm_password_field.fill(TEST_PASSWORD)

    page.wait_for_timeout(1000)

    page.screenshot(
        path="runtime/screenshots/tc031_password_values_entered.png"
    )

    # --------------------------------------------------
    # Validate Field Masking
    # --------------------------------------------------

    new_password_type = new_password_field.evaluate(
        "e => e.getAttribute('type')"
    )

    confirm_password_type = confirm_password_field.evaluate(
        "e => e.getAttribute('type')"
    )

    log(f"New Password field type=[{new_password_type}]")
    log(f"Confirm Password field type=[{confirm_password_type}]")

    if new_password_type != "password":
        raise Exception(
            "New Password field is not masked. "
            f"Expected type=[password], got [{new_password_type}]"
        )

    if confirm_password_type != "password":
        raise Exception(
            "Confirm Password field is not masked. "
            f"Expected type=[password], got [{confirm_password_type}]"
        )

    # Optional diagnostic:
    # input_value() can still read the DOM value, but UI masking is controlled
    # by input type=password. So we do not fail if DOM value is readable by automation.
    new_password_value = new_password_field.input_value()
    confirm_password_value = confirm_password_field.input_value()

    log(
        "Automation can read password input value from DOM, "
        "but browser UI masking is controlled by type=password"
    )

    if new_password_value != TEST_PASSWORD:
        raise Exception(
            "New Password input value was not set correctly"
        )

    if confirm_password_value != TEST_PASSWORD:
        raise Exception(
            "Confirm Password input value was not set correctly"
        )

    log(
        "OTCT-7968_TC_031 PASSED - Password and Confirm Password "
        "fields are masked using input type=password"
    )

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()