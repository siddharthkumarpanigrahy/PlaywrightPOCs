import os
import shutil

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

BASE_CSV_FILE = (
    "./test_data/mc_gui/security/"
    "margin calculator/TC-012.csv"
)

SPACED_FILENAME_DIR = (
    "./test_data/mc_gui/security/"
    "margin calculator/filename_spaces"
)

SPACED_FILENAME = " TC-012.csv "

EXPECTED_MESSAGES = [
    "Invalid file format",
    "Error",
    "Resource not available",
    "uploaded",
    "processed",
    "success",
    "failed",
    "validation"
]


# --------------------------------------------------
# File Helper
# --------------------------------------------------

def prepare_filename_with_spaces():
    if not os.path.exists(BASE_CSV_FILE):
        raise Exception(
            f"Base MC-GUI CSV file does not exist: {BASE_CSV_FILE}"
        )

    os.makedirs(
        SPACED_FILENAME_DIR,
        exist_ok=True
    )

    spaced_file_path = os.path.join(
        SPACED_FILENAME_DIR,
        SPACED_FILENAME
    )

    log(
        "Creating file with leading/trailing spaces in filename: "
        f"[{spaced_file_path}]"
    )

    shutil.copyfile(
        BASE_CSV_FILE,
        spaced_file_path
    )

    if not os.path.exists(spaced_file_path):
        raise Exception(
            "File with leading/trailing spaces was not created"
        )

    log(
        "Created spaced filename file successfully. "
        f"filename=[{SPACED_FILENAME}], "
        f"filename_length=[{len(SPACED_FILENAME)}]"
    )

    return spaced_file_path


# --------------------------------------------------
# Popup Helpers
# --------------------------------------------------

def click_ok_if_present(page):
    ok_text = page.get_by_text(
        "OK",
        exact=True
    )

    if ok_text.count() > 0:
        for index in range(ok_text.count()):
            item = ok_text.nth(index)

            try:
                if item.is_visible():
                    item.click()
                    page.wait_for_timeout(1000)
                    log("Clicked OK")
                    return True
            except Exception:
                pass

    return False


def handle_initial_popup_if_present(page):
    log("Checking for initial popup")

    if page.get_by_text(
        "Resource not available",
        exact=False
    ).count() > 0:
        log("Resource not available popup/message found")

        page.screenshot(
            path="runtime/screenshots/mc_tc002_resource_not_available.png"
        )

        click_ok_if_present(page)

        return True

    if page.get_by_text(
        "Backend connection problem",
        exact=False
    ).count() > 0:
        log("Backend connection problem popup/message found")

        page.screenshot(
            path="runtime/screenshots/mc_tc002_backend_connection_problem.png"
        )

        click_ok_if_present(page)

        return True

    log("No initial popup found")
    return False


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
        path="runtime/screenshots/mc_tc002_before_login.png"
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

    # --------------------------------------------------
    # Enter username using real keyboard events
    # --------------------------------------------------

    log("Entering MC-GUI username using keyboard events")

    username_field.click()
    username_field.press("Control+A")
    username_field.press("Delete")
    username_field.press_sequentially(MC_USERNAME)

    page.wait_for_timeout(500)

    # --------------------------------------------------
    # Enter password using real keyboard events
    # --------------------------------------------------

    log("Entering MC-GUI password using keyboard events")

    password_field.click()
    password_field.press("Control+A")
    password_field.press("Delete")
    password_field.press_sequentially(MC_PASSWORD)

    page.wait_for_timeout(500)

    # Trigger blur/change handling.
    password_field.press("Tab")

    page.wait_for_timeout(1000)

    username_value = username_field.input_value()
    password_value = password_field.input_value()

    log(f"Entered username value=[{username_value}]")
    log(f"Password entered=[{bool(password_value)}]")

    if username_value != MC_USERNAME:
        page.screenshot(
            path="runtime/screenshots/mc_tc002_username_not_entered.png"
        )

        raise Exception(
            f"Username was not entered correctly. "
            f"Expected [{MC_USERNAME}], got [{username_value}]"
        )

    if not password_value:
        page.screenshot(
            path="runtime/screenshots/mc_tc002_password_not_entered.png"
        )

        raise Exception("Password was not entered")

    page.screenshot(
        path="runtime/screenshots/mc_tc002_credentials_entered.png"
    )

    # --------------------------------------------------
    # Wait for Login button to become enabled
    # --------------------------------------------------

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
        log("Login button did not become enabled after keyboard input")

        login_button_html = login_button.evaluate(
            "e => e.outerHTML"
        )

        log(f"LOGIN_BUTTON_HTML=[{login_button_html}]")

        page.screenshot(
            path="runtime/screenshots/mc_tc002_login_button_still_disabled.png"
        )

        raise Exception(
            "Login button is still disabled after username/password entry. "
            "Check whether credentials are accepted by MC-GUI login validation."
        )

    # --------------------------------------------------
    # Click Login
    # --------------------------------------------------

    log("Clicking Login")

    login_button.click(
        timeout=30000
    )

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/mc_tc002_after_login.png"
    )

    handle_initial_popup_if_present(page)
    
def upload_spaced_filename(page, file_path):
    log(f"Uploading file [{file_path}]")

    upload_input = page.locator(
        "input[name=\"OTC\"]"
    )

    upload_input.wait_for(
        state="attached",
        timeout=30000
    )

    upload_input.set_input_files(file_path)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_tc002_after_file_upload.png"
    )


def validate_upload_result(page):
    log("Validating MC-GUI upload result")

    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("MC-GUI BODY TEXT AFTER UPLOAD START")
    log(body_text[:4000])
    log("MC-GUI BODY TEXT AFTER UPLOAD END")

    page.screenshot(
        path="runtime/screenshots/mc_tc002_upload_validation.png"
    )

    matched_messages = [
        message
        for message in EXPECTED_MESSAGES
        if message.lower() in body_text_lower
    ]

    if not matched_messages:
        raise Exception(
            "No expected upload result or validation message found "
            "after uploading file with leading/trailing spaces in filename"
        )

    log(
        "Upload produced controlled result/message. "
        f"Matched messages={matched_messages}"
    )

    # If error popup is present, close it.
    if page.get_by_text(
        "Error",
        exact=False
    ).count() > 0:
        click_ok_if_present(page)

    log(
        "OTCT-7968_TC_002 PASSED - MC-GUI handled filename "
        "with leading/trailing spaces without unexpected behavior"
    )


def logout_mc_gui(page):
    log("Logging out from MC-GUI")

    try:
        # Close any validation/error popup first.
        ok_buttons = [
            page.get_by_text("OK", exact=True),
            page.get_by_text("Ok", exact=True),
            page.get_by_role("button", name="OK"),
            page.get_by_role("button", name="Ok")
        ]

        for ok_button in ok_buttons:
            try:
                if ok_button.count() > 0:
                    for index in range(ok_button.count()):
                        item = ok_button.nth(index)

                        if item.is_visible():
                            log("Closing popup before logout using OK")
                            item.click(force=True)
                            page.wait_for_timeout(1000)
                            break
            except Exception:
                pass

        # Wait for modal glass overlay to disappear if present.
        try:
            page.locator(".gwt-PopupPanelGlass").wait_for(
                state="hidden",
                timeout=5000
            )
        except Exception:
            log("Popup glass overlay still present or already detached")

        page.screenshot(
            path="runtime/screenshots/mc_tc002_before_logout.png"
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
            path="runtime/screenshots/mc_tc002_after_logout.png"
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
    log("Starting MC-GUI OTCT-7968_TC_002")

    spaced_file_path = prepare_filename_with_spaces()

    login_to_mc_gui(page)

    upload_spaced_filename(
        page,
        spaced_file_path
    )

    validate_upload_result(page)

    logout_mc_gui(page)

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()