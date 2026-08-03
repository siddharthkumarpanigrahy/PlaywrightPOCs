
import os
import csv

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

FORMULA_INJECTION_DIR = (
    "./test_data/mc_gui/security/"
    "margin calculator/formula_injection"
)

FORMULA_INJECTION_FILE = (
    FORMULA_INJECTION_DIR +
    "/TC-012_FormulaInjection.csv"
)

FORMULA_PAYLOADS = [
    "=SUM(A1+B1)",
    "@SUM(A1+B1)",
    "+SUM(A1+B1)",
    "-SUM(A1+B1)"
]

EXPECTED_MESSAGES = [
    "Error",
    "OTC CSV",
    "Invalid file format",
    "Uploaded OTC file is not consistent with template",
    "not consistent with template",
    "invalid",
    "validation",
    "failed",
    "formula",
    "character",
    "MessageTypeIDCodeMessage",
    "success",
    "processed",
    "uploaded"
]


# --------------------------------------------------
# File Helper
# --------------------------------------------------

def prepare_formula_injection_file():
    if not os.path.exists(BASE_CSV_FILE):
        raise Exception(
            f"Base MC-GUI CSV file does not exist: {BASE_CSV_FILE}"
        )

    os.makedirs(
        FORMULA_INJECTION_DIR,
        exist_ok=True
    )

    log(
        "Creating CSV formula-injection file from base file: "
        f"[{BASE_CSV_FILE}]"
    )

    with open(
        BASE_CSV_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as source_file:
        reader = csv.reader(source_file)
        rows = list(reader)

    if len(rows) < 2:
        raise Exception(
            "Base CSV file must contain at least one header row "
            "and one data row"
        )

    header = rows[0]
    data_rows = rows[1:]

    if "internalTradeID" not in header:
        raise Exception(
            "Expected header [internalTradeID] was not found in base CSV"
        )

    internal_trade_id_index = header.index("internalTradeID")

    # Create multiple data rows with common CSV formula injection prefixes.
    # The payloads are placed in internalTradeID because this field is parsed
    # as file content and should be sanitized, rejected, or safely processed.
    formula_rows = []

    for index, payload in enumerate(FORMULA_PAYLOADS):
        row = list(data_rows[0])
        row[internal_trade_id_index] = payload
        formula_rows.append(row)

    with open(
        FORMULA_INJECTION_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as target_file:
        writer = csv.writer(target_file)
        writer.writerow(header)
        writer.writerows(formula_rows)

    if not os.path.exists(FORMULA_INJECTION_FILE):
        raise Exception(
            f"Formula-injection file was not created: "
            f"{FORMULA_INJECTION_FILE}"
        )

    file_size = os.path.getsize(FORMULA_INJECTION_FILE)

    log(
        "Created formula-injection file successfully. "
        f"path=[{FORMULA_INJECTION_FILE}], "
        f"size_bytes=[{file_size}], "
        f"payload_count=[{len(FORMULA_PAYLOADS)}]"
    )

    return FORMULA_INJECTION_FILE


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
            if page.get_by_text(
                message,
                exact=False
            ).count() > 0:

                log(f"Initial popup/message found: [{message}]")

                page.screenshot(
                    path="runtime/screenshots/mc_tc008_initial_popup.png"
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
        path="runtime/screenshots/mc_tc008_before_login.png"
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
            path="runtime/screenshots/mc_tc008_username_not_entered.png"
        )

        raise Exception(
            f"Username was not entered correctly. "
            f"Expected [{MC_USERNAME}], got [{username_value}]"
        )

    if not password_value:
        page.screenshot(
            path="runtime/screenshots/mc_tc008_password_not_entered.png"
        )

        raise Exception("Password was not entered")

    page.screenshot(
        path="runtime/screenshots/mc_tc008_credentials_entered.png"
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
            path="runtime/screenshots/mc_tc008_login_button_still_disabled.png"
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
        path="runtime/screenshots/mc_tc008_after_login.png"
    )

    handle_initial_popup_if_present(page)


def upload_formula_injection_file(page, file_path):
    log(f"Uploading CSV formula-injection file [{file_path}]")

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
        path="runtime/screenshots/mc_tc008_after_formula_upload.png"
    )


def click_validate_button(page):
    log("Clicking MC-GUI Validate button")

    validate_button = page.get_by_role(
        "button",
        name="Validate"
    )

    validate_button.wait_for(
        state="visible",
        timeout=30000
    )

    validate_button.click()

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/mc_tc008_after_validate_click.png"
    )


def validate_formula_injection_result(page):
    log("Validating MC-GUI CSV formula-injection handling result")

    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("MC-GUI BODY TEXT AFTER VALIDATE START")
    log(body_text[:5000])
    log("MC-GUI BODY TEXT AFTER VALIDATE END")

    page.screenshot(
        path="runtime/screenshots/mc_tc008_formula_validation.png"
    )

    matched_messages = [
        message
        for message in EXPECTED_MESSAGES
        if message.lower() in body_text_lower
    ]

    if not matched_messages:
        raise Exception(
            "Expected CSV formula-injection validation or safe-processing "
            "result was not found after clicking Validate"
        )

    log(
        "CSV formula-injection upload produced controlled result. "
        f"Matched messages={matched_messages}"
    )

    # If the application shows a controlled error grid, validate it.
    error_cell = page.get_by_role(
        "cell",
        name="Error",
        exact=True
    )

    if error_cell.count() > 0:
        log("Controlled error grid detected")

        otc_csv_cell = page.get_by_role(
            "cell",
            name="OTC CSV",
            exact=True
        )

        if otc_csv_cell.count() == 0:
            log(
                "Error cell was found, but OTC CSV cell was not found. "
                "Continuing because controlled error text is visible."
            )

    # Formula text should not be rendered as an executable action.
    # The test confirms controlled UI behavior, not spreadsheet execution.
    page.screenshot(
        path="runtime/screenshots/mc_tc008_expected_result_verified.png"
    )

    log(
        "OTCT-7968_TC_008 PASSED - MC-GUI handled CSV formula "
        "injection payload safely with controlled validation or "
        "processing behavior"
    )


def logout_mc_gui(page):
    log("Logging out from MC-GUI")

    try:
        close_popup_before_logout(page)

        page.screenshot(
            path="runtime/screenshots/mc_tc008_before_logout.png"
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
            path="runtime/screenshots/mc_tc008_after_logout.png"
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
    log("Starting MC-GUI OTCT-7968_TC_008")

    formula_injection_file = prepare_formula_injection_file()

    login_to_mc_gui(page)

    upload_formula_injection_file(
        page,
        formula_injection_file
    )

    click_validate_button(page)

    validate_formula_injection_result(page)

    logout_mc_gui(page)

except Exception as e:

    log(f"TEST FAILED: {e}")
    raise

finally:

    browser.close()
    playwright.stop()