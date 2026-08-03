
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

UPLOAD_FILE = (
    "./test_data/otc_gui/security/"
    "margin calculator/TC-012.csv"
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def click_first_visible(page, selectors, description, required=False):
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
                    item.click()
                    page.wait_for_timeout(1000)
                    return True
            except Exception:
                pass

    if required:
        page.screenshot(
            path=f"runtime/screenshots/mc_gui_{description}_not_found.png"
        )

        body_text = page.locator("body").inner_text()
        log(f"BODY TEXT WHEN [{description}] NOT FOUND START")
        log(body_text[:3000])
        log(f"BODY TEXT WHEN [{description}] NOT FOUND END")

        raise Exception(
            f"Required element not found: {description}"
        )

    log(f"[{description}] not found, continuing")
    return False


def fill_first_visible(page, selectors, value, description, required=True):
    log(f"Looking for input [{description}]")

    for selector in selectors:
        locator = page.locator(selector)

        if locator.count() == 0:
            continue

        for index in range(locator.count()):
            item = locator.nth(index)

            try:
                if item.is_visible():
                    log(
                        f"Found visible input [{description}] "
                        f"using selector [{selector}]"
                    )
                    item.click()
                    item.fill(value)
                    page.wait_for_timeout(500)
                    return True
            except Exception:
                pass

    if required:
        page.screenshot(
            path=f"runtime/screenshots/mc_gui_{description}_input_not_found.png"
        )

        body_text = page.locator("body").inner_text()
        log(f"BODY TEXT WHEN INPUT [{description}] NOT FOUND START")
        log(body_text[:3000])
        log(f"BODY TEXT WHEN INPUT [{description}] NOT FOUND END")

        raise Exception(
            f"Required input not found: {description}"
        )

    return False


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
        path="runtime/screenshots/mc_gui_before_login.png"
    )

    page.pause()  # Pause for manual inspection if needed

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
        path="runtime/screenshots/mc_gui_after_login.png"
    )

    handle_initial_popup_if_present(page)


def upload_mc_file(page):
    log("Preparing MC-GUI file upload")

    if not os.path.exists(UPLOAD_FILE):
        raise Exception(
            f"Upload file does not exist: {UPLOAD_FILE}"
        )

    # TODO:
    # Replace this candidate list after you provide Codegen/Inspector locators.
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
            path="runtime/screenshots/mc_gui_file_upload_input_not_found.png"
        )

        body_text = page.locator("body").inner_text()

        log("BODY TEXT WHEN FILE UPLOAD INPUT NOT FOUND START")
        log(body_text[:4000])
        log("BODY TEXT WHEN FILE UPLOAD INPUT NOT FOUND END")

        raise Exception(
            "File upload input was not found. "
            "Please provide Codegen locator for MC-GUI upload control."
        )

    log(f"Uploading file [{UPLOAD_FILE}]")

    upload_input.set_input_files(UPLOAD_FILE)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_gui_after_file_selected.png"
    )


def click_upload_or_submit_if_present(page):
    log("Looking for Upload/Submit/Calculate button")

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
            "The application may auto-upload after file selection."
        )

    page.screenshot(
        path="runtime/screenshots/mc_gui_after_upload_action.png"
    )


def validate_upload_popup_or_message(page):
    log("Validating MC-GUI upload popup/message")

    body_text = page.locator("body").inner_text()

    log("MC-GUI BODY TEXT AFTER UPLOAD START")
    log(body_text[:4000])
    log("MC-GUI BODY TEXT AFTER UPLOAD END")

    page.screenshot(
        path="runtime/screenshots/mc_gui_upload_message_validation.png"
    )

    message_keywords = [
        "error",
        "invalid",
        "success",
        "uploaded",
        "processed",
        "failed",
        "validation",
        "file",
        "csv",
        "trade"
    ]

    body_text_lower = body_text.lower()

    if any(keyword in body_text_lower for keyword in message_keywords):
        log(
            "MC-GUI upload produced visible message/result. "
            "Skeleton validation completed."
        )
        return

    raise Exception(
        "No recognizable upload message/result found. "
        "Please provide exact validation popup/message from Codegen run."
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
    log("Starting MC-GUI upload skeleton for OTCT-7968")

    login_to_mc_gui(page)

    # Optional pause if you want to inspect manually before upload.
    # Uncomment this while collecting locators:
    # page.pause()

    upload_mc_file(page)

    click_upload_or_submit_if_present(page)

    validate_upload_popup_or_message(page)

    log(
        "MC-GUI upload skeleton completed. "
        "Provide Codegen locators next so we can convert this "
        "into the exact TC001 long-filename test."
    )

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()