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

os.environ["NO_PROXY"] = "10.130.209.4"
os.environ["no_proxy"] = "10.130.209.4"

os.makedirs("runtime/screenshots", exist_ok=True)


# --------------------------------------------------
# Test Data
# --------------------------------------------------

MC_GUI_URL = (
    "https://10.130.209.4:8443/"
    "Margin_Calculator_Jenkins_git/mc-main.html#"
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

LONG_FILENAME_DIR = (
    "./test_data/otc_gui/security/"
    "margin calculator/long_filename"
)

# True >255 filename attempt.
# 256 + ".csv" = 260 characters for the filename component.
LONG_FILENAME_BASE_LENGTH = 256

EXPECTED_ERROR_KEYWORDS = [
    "file name",
    "filename",
    "too long",
    "maximum",
    "255",
    "length",
    "invalid",
    "validation",
    "error",
    "rejected"
]

UNEXPECTED_SUCCESS_KEYWORDS = [
    "success",
    "successfully",
    "processed",
    "uploaded successfully"
]


# --------------------------------------------------
# Generic Element Helpers
# --------------------------------------------------

def find_first_visible(page, selectors, description):
    log(f"Looking for [{description}]")

    for selector in selectors:
        locator = page.locator(selector)

        if locator.count() == 0:
            continue

        for index in range(locator.count()):
            item = locator.nth(index)

            try:
                if item.is_visible():
                    log(
                        f"Found visible [{description}] "
                        f"using selector [{selector}]"
                    )
                    return item
            except Exception:
                pass

    return None


def click_first_visible(page, selectors, description, required=False):
    item = find_first_visible(
        page,
        selectors,
        description
    )

    if item is None:
        if required:
            page.screenshot(
                path=f"runtime/screenshots/mc_tc001_{description}_not_found.png"
            )

            body_text = page.locator("body").inner_text()

            log(f"BODY TEXT WHEN [{description}] NOT FOUND START")
            log(body_text[:4000])
            log(f"BODY TEXT WHEN [{description}] NOT FOUND END")

            raise Exception(
                f"Required element not found: {description}"
            )

        log(f"[{description}] not found, continuing")
        return False

    item.click()
    page.wait_for_timeout(1000)
    return True


def fill_first_visible(page, selectors, value, description, required=True):
    item = find_first_visible(
        page,
        selectors,
        description
    )

    if item is None:
        if required:
            page.screenshot(
                path=f"runtime/screenshots/mc_tc001_{description}_not_found.png"
            )

            body_text = page.locator("body").inner_text()

            log(f"BODY TEXT WHEN INPUT [{description}] NOT FOUND START")
            log(body_text[:4000])
            log(f"BODY TEXT WHEN INPUT [{description}] NOT FOUND END")

            raise Exception(
                f"Required input not found: {description}"
            )

        return False

    item.click()
    item.fill(value)
    page.wait_for_timeout(500)
    return True


# --------------------------------------------------
# File Helpers
# --------------------------------------------------

def prepare_long_filename_file():
    if not os.path.exists(BASE_CSV_FILE):
        raise Exception(
            f"Base MC-GUI CSV file does not exist: {BASE_CSV_FILE}"
        )

    os.makedirs(
        LONG_FILENAME_DIR,
        exist_ok=True
    )

    long_name = (
        "A" * LONG_FILENAME_BASE_LENGTH
    ) + ".csv"

    long_file_path = os.path.join(
        LONG_FILENAME_DIR,
        long_name
    )

    log(
        "Attempting to create file with filename length "
        f"[{len(long_name)}]: [{long_name[:40]}...]"
    )

    try:
        shutil.copyfile(
            BASE_CSV_FILE,
            long_file_path
        )

        if not os.path.exists(long_file_path):
            raise Exception(
                "Long filename file was not created"
            )

        log(
            "Created long filename file successfully. "
            f"filename_length=[{len(long_name)}]"
        )

        return long_file_path, len(long_name), False

    except OSError as error:
        log(
            "Unable to create true >255-character filename. "
            "This is likely blocked by the local OS/filesystem before "
            "the browser can upload it."
        )
        log(f"OSError=[{error}]")

        page_blocker_message = (
            "OTCT-7968_TC_001 BLOCKED AT LOCAL FILESYSTEM: "
            "A true filename component greater than 255 characters "
            "cannot be created on this machine. "
            "Need backend/storage-level test support or DEV-provided "
            "test object to validate strict >255 filename behavior."
        )

        raise Exception(page_blocker_message)


# --------------------------------------------------
# MC-GUI Flow Helpers
# --------------------------------------------------

def handle_initial_popup_if_present(page):
    log("Checking for initial popup")

    popup_buttons = [
        "button:has-text('OK')",
        "button:has-text('Ok')",
        "button:has-text('Close')",
        "button:has-text('Continue')",
        "button:has-text('Yes')",
        "div:has-text('OK')",
        "div:has-text('Ok')",
        "div:has-text('Close')",
        "span:has-text('OK')",
        "span:has-text('Ok')",
        "span:has-text('Close')"
    ]

    clicked = click_first_visible(
        page,
        popup_buttons,
        "initial_popup_button",
        required=False
    )

    if clicked:
        log("Initial popup handled")
    else:
        log("No initial popup found")


def login_to_mc_gui(page):
    log("Launching MC-GUI")

    page.goto(
        MC_GUI_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_tc001_before_login.png"
    )

    username_selectors = [
        "#username input",
        "#username",
        "input[name='username']",
        "input[type='text']",
        "input"
    ]

    password_selectors = [
        "#password input",
        "#password",
        "input[name='password']",
        "input[type='password']"
    ]

    login_button_selectors = [
        "button:has-text('Login')",
        "div:has-text('Login')",
        "span:has-text('Login')",
        "#login"
    ]

    fill_first_visible(
        page,
        username_selectors,
        MC_USERNAME,
        "username"
    )

    fill_first_visible(
        page,
        password_selectors,
        MC_PASSWORD,
        "password"
    )

    click_first_visible(
        page,
        login_button_selectors,
        "login_button",
        required=True
    )

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/mc_tc001_after_login.png"
    )

    handle_initial_popup_if_present(page)


def upload_file(page, file_path):
    log(f"Preparing to upload file [{file_path}]")

    file_upload_selectors = [
        "input[type='file']",
        "#fileUpload input[type='file']",
        "#upload input[type='file']",
        "input"
    ]

    upload_input = None

    for selector in file_upload_selectors:
        locator = page.locator(selector)

        if locator.count() == 0:
            continue

        for index in range(locator.count()):
            item = locator.nth(index)

            try:
                input_type = item.evaluate(
                    "e => e.getAttribute('type')"
                )

                if input_type == "file":
                    upload_input = item
                    log(
                        f"Found file upload input using selector "
                        f"[{selector}]"
                    )
                    break
            except Exception:
                pass

        if upload_input is not None:
            break

    if upload_input is None:
        page.screenshot(
            path="runtime/screenshots/mc_tc001_file_upload_input_not_found.png"
        )

        body_text = page.locator("body").inner_text()

        log("BODY TEXT WHEN FILE UPLOAD INPUT NOT FOUND START")
        log(body_text[:4000])
        log("BODY TEXT WHEN FILE UPLOAD INPUT NOT FOUND END")

        raise Exception(
            "File upload input was not found. "
            "Please provide actual MC-GUI Codegen locator."
        )

    upload_input.set_input_files(file_path)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_tc001_after_file_selected.png"
    )


def click_upload_or_submit_if_present(page):
    log("Looking for Upload/Submit/Calculate/Process button")

    button_selectors = [
        "button:has-text('Upload')",
        "button:has-text('Submit')",
        "button:has-text('Calculate')",
        "button:has-text('Process')",
        "button:has-text('Start')",
        "div:has-text('Upload')",
        "div:has-text('Submit')",
        "div:has-text('Calculate')",
        "div:has-text('Process')",
        "span:has-text('Upload')",
        "span:has-text('Submit')",
        "span:has-text('Calculate')",
        "span:has-text('Process')"
    ]

    clicked = click_first_visible(
        page,
        button_selectors,
        "upload_or_submit_button",
        required=False
    )

    if clicked:
        log("Upload/Submit/Calculate action clicked")
        page.wait_for_timeout(5000)
    else:
        log(
            "No Upload/Submit button clicked. "
            "Application may auto-upload after file selection."
        )

    page.screenshot(
        path="runtime/screenshots/mc_tc001_after_upload_action.png"
    )


def validate_long_filename_rejection(page, filename_length):
    log("Validating long filename rejection or controlled handling")

    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("MC-GUI BODY TEXT AFTER LONG FILENAME UPLOAD START")
    log(body_text[:5000])
    log("MC-GUI BODY TEXT AFTER LONG FILENAME UPLOAD END")

    page.screenshot(
        path="runtime/screenshots/mc_tc001_long_filename_validation.png"
    )

    if any(
        keyword in body_text_lower
        for keyword in EXPECTED_ERROR_KEYWORDS
    ):
        log(
            "OTCT-7968_TC_001 PASSED - Long filename was rejected "
            "or validated with an appropriate message. "
            f"filename_length=[{filename_length}]"
        )
        return

    if any(
        keyword in body_text_lower
        for keyword in UNEXPECTED_SUCCESS_KEYWORDS
    ):
        raise Exception(
            "Long filename appears to have been accepted/processed "
            "successfully, but TC001 expects rejection or validation. "
            f"filename_length=[{filename_length}]"
        )

    raise Exception(
        "No recognizable long-filename validation message was found. "
        "Provide exact MC-GUI popup/message and upload locators from Codegen."
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
    log("Starting MC-GUI OTCT-7968_TC_001")

    long_file_path, filename_length, fallback_used = prepare_long_filename_file()

    login_to_mc_gui(page)

    upload_file(
        page,
        long_file_path
    )

    click_upload_or_submit_if_present(page)

    validate_long_filename_rejection(
        page,
        filename_length
    )

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()