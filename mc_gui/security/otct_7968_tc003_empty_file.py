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

MC_GUI_URL = (
    "https://10.130.209.10:8443/"
    "Margin_Calculator_Jenkins_git/"
)

MC_USERNAME = os.getenv(
    "MC_USERNAME",
    "CBKFRCLR001"
)

MC_PASSWORD = os.getenv(
    "MC_PASSWORD",
    "CBKFRCLR001"
)

EMPTY_FILE = (
    "./test_data/mc_gui/security/"
    "margin calculator/EmptyFile.csv"
)

EXPECTED_MESSAGES = [
    "Invalid file format",
    "File is empty",
    "empty file",
    "0 bytes",
    "Error",
    "validation",
    "invalid",
    "failed"
]


# --------------------------------------------------
# File Helper
# --------------------------------------------------

def prepare_empty_file():
    folder = os.path.dirname(EMPTY_FILE)

    if folder:
        os.makedirs(folder, exist_ok=True)

    log(f"Preparing empty file at [{EMPTY_FILE}]")

    with open(EMPTY_FILE, "w", encoding="utf-8"):
        pass

    if not os.path.exists(EMPTY_FILE):
        raise Exception(
            f"Empty file was not created: {EMPTY_FILE}"
        )

    file_size = os.path.getsize(EMPTY_FILE)

    if file_size != 0:
        raise Exception(
            f"Expected empty file size [0], got [{file_size}]"
        )

    log(
        f"Empty file prepared successfully. "
        f"path=[{EMPTY_FILE}], size_bytes=[{file_size}]"
    )


# --------------------------------------------------
# Popup Helpers
# --------------------------------------------------

def click_ok_if_present(page):
    ok_candidates = [
        page.get_by_text("OK", exact=True),
        page.get_by_text("Ok", exact=True),
        page.get_by_role("button", name="OK"),
        page.get_by_role("button", name="Ok")
    ]

    for ok_candidate in ok_candidates:
        try:
            if ok_candidate.count() > 0:
                for index in range(ok_candidate.count()):
                    item = ok_candidate.nth(index)

                    if item.is_visible():
                        log("Clicking OK")
                        item.click(force=True)
                        page.wait_for_timeout(1000)
                        return True
        except Exception:
            pass

    return False


def handle_initial_popup_if_present(page):
    log("Checking for initial popup")

    popup_messages = [
        "Resource not available",
        "Backend connection problem",
        "Error"
    ]

    for message in popup_messages:
        try:
            if page.get_by_text(message, exact=False).count() > 0:
                log(f"Initial popup/message found: [{message}]")

                page.screenshot(
                    path="runtime/screenshots/mc_tc003_initial_popup.png"
                )

                click_ok_if_present(page)

                return True
        except Exception:
            pass

    log("No initial popup found")
    return False


def close_popup_before_logout(page):
    click_ok_if_present(page)

    try:
        page.locator(".gwt-PopupPanelGlass").wait_for(
            state="hidden",
            timeout=5000
        )
    except Exception:
        log("Popup glass overlay still present or already detached")


# --------------------------------------------------
# MC-GUI Flow
# --------------------------------------------------

def login_to_mc_gui(page):
    log("Launching MC-GUI")

    page.goto(
        MC_GUI_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_tc003_before_login.png"
    )

    log(f"Using MC-GUI username [{MC_USERNAME}]")

    username_field = page.locator("#loginID")
    password_field = page.locator("#pwd")
    login_button = page.locator("#doLogin")

    username_field.wait_for(
        state="visible",
        timeout=30000
    )

    password_field.wait_for(
        state="visible",
        timeout=30000
    )

    log("Entering MC-GUI username using keyboard events")

    username_field.click()
    username_field.press("Control+A")
    username_field.press("Delete")
    username_field.press_sequentially(MC_USERNAME)

    page.wait_for_timeout(500)

    log("Entering MC-GUI password using keyboard events")

    password_field.click()
    password_field.press("Control+A")
    password_field.press("Delete")
    password_field.press_sequentially(MC_PASSWORD)

    page.wait_for_timeout(500)

    password_field.press("Tab")

    page.wait_for_timeout(1000)

    username_value = username_field.input_value()
    password_value = password_field.input_value()

    log(f"Entered username value=[{username_value}]")
    log(f"Password entered=[{bool(password_value)}]")

    if username_value != MC_USERNAME:
        page.screenshot(
            path="runtime/screenshots/mc_tc003_username_not_entered.png"
        )

        raise Exception(
            f"Username was not entered correctly. "
            f"Expected [{MC_USERNAME}], got [{username_value}]"
        )

    if not password_value:
        page.screenshot(
            path="runtime/screenshots/mc_tc003_password_not_entered.png"
        )

        raise Exception("Password was not entered")

    page.screenshot(
        path="runtime/screenshots/mc_tc003_credentials_entered.png"
    )

    log("Waiting for Login button to become enabled")

    try:
        page.wait_for_function(
            """
            () => {
                const button = document.querySelector('#doLogin');
                return button && !button.disabled;
            }
            """,
            timeout=10000
        )
    except Exception:
        login_button_html = login_button.evaluate(
            "e => e.outerHTML"
        )

        log(f"LOGIN_BUTTON_HTML=[{login_button_html}]")

        page.screenshot(
            path="runtime/screenshots/mc_tc003_login_button_still_disabled.png"
        )

        raise Exception(
            "Login button is still disabled after username/password entry"
        )

    log("Clicking Login")

    login_button.click(
        timeout=30000
    )

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/mc_tc003_after_login.png"
    )

    handle_initial_popup_if_present(page)


def upload_empty_file(page):
    log(f"Uploading empty file [{EMPTY_FILE}]")

    upload_input = page.locator(
        "input[name=\"OTC\"]"
    )

    upload_input.wait_for(
        state="attached",
        timeout=30000
    )

    upload_input.set_input_files(EMPTY_FILE)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_tc003_after_empty_file_upload.png"
    )


def validate_empty_file_result(page):
    log("Validating MC-GUI empty file validation result")

    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("MC-GUI BODY TEXT AFTER EMPTY FILE UPLOAD START")
    log(body_text[:4000])
    log("MC-GUI BODY TEXT AFTER EMPTY FILE UPLOAD END")

    page.screenshot(
        path="runtime/screenshots/mc_tc003_empty_file_validation.png"
    )

    matched_messages = [
        message
        for message in EXPECTED_MESSAGES
        if message.lower() in body_text_lower
    ]

    if not matched_messages:
        raise Exception(
            "No expected empty-file validation message found "
            "after uploading empty file"
        )

    log(
        "Empty file upload produced controlled validation/result. "
        f"Matched messages={matched_messages}"
    )

    click_ok_if_present(page)

    log(
        "OTCT-7968_TC_003 PASSED - MC-GUI rejected empty file "
        "with expected validation behavior"
    )


def logout_mc_gui(page):
    log("Logging out from MC-GUI")

    try:
        close_popup_before_logout(page)

        page.screenshot(
            path="runtime/screenshots/mc_tc003_before_logout.png"
        )

        logout_button = page.get_by_role(
            "button",
            name="Logout"
        )

        logout_button.wait_for(
            state="visible",
            timeout=10000
        )

        logout_button.click(force=True)

        page.wait_for_timeout(2000)

        page.screenshot(
            path="runtime/screenshots/mc_tc003_after_logout.png"
        )

        log("Logout completed")

    except Exception as error:
        log(f"Logout skipped or failed: {error}")


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
    log("Starting MC-GUI OTCT-7968_TC_003")

    prepare_empty_file()

    login_to_mc_gui(page)

    upload_empty_file(page)

    validate_empty_file_result(page)

    logout_mc_gui(page)

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()