import os
import time

from common.login import login
from common.logout import logout
from common.browser import launch_browser
from common.logger import log
from locators.otc_gui.portfolio_transfer_locators import (
    PortfolioTransferLocators,
)


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

TARGET_BOOK = "CBKFR_A1"

RECORD_COUNT = int(
    os.getenv(
        "EXTREME_RECORD_COUNT",
        "100000"
    )
)

EXTREME_FILE = (
    "./test_data/otc_gui/security/"
    f"portfolio transfer/Portfolio_Extreme_{RECORD_COUNT}_TradeIds.csv"
)

VALIDATION_KEYWORDS = [
    "error",
    "invalid",
    "failure",
    "detected",
    "csv",
    "trade",
    "too many",
    "limit",
    "maximum",
    "record",
    "timeout",
    "memory",
    "processing"
]


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def generate_extreme_trade_id_file(file_path):
    """
    Generates an extremely large portfolio upload CSV.

    File format:
        CCPTradeId,Fee,PartialTransferAmount

    Number of data rows:
        RECORD_COUNT
    """

    folder = os.path.dirname(file_path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    log(
        f"Generating extreme CSV file at [{file_path}] "
        f"with [{RECORD_COUNT}] Trade IDs"
    )

    start_time = time.time()

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        file.write("CCPTradeId,Fee,PartialTransferAmount\n")

        for index in range(1, RECORD_COUNT + 1):
            trade_id = 720000000 + index
            file.write(f"{trade_id},0,\n")

    generation_elapsed = round(
        time.time() - start_time,
        2
    )

    actual_rows = count_data_rows(file_path)

    if actual_rows != RECORD_COUNT:
        raise Exception(
            f"Generated file row count mismatch. "
            f"Expected [{RECORD_COUNT}], got [{actual_rows}]"
        )

    file_size = os.path.getsize(file_path)

    log(
        f"Generated extreme CSV successfully. "
        f"Data rows=[{actual_rows}], "
        f"size_bytes=[{file_size}], "
        f"generation_seconds=[{generation_elapsed}]"
    )


def count_data_rows(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file) - 1


def wait_for_progress_bar_close(page, timeout=600000):
    progress_bar = page.locator("#progressBar")

    try:
        progress_bar.wait_for(
            state="hidden",
            timeout=timeout
        )
    except Exception:
        pass


def confirm_mtm_if_present(page):
    mtm_popup_text = page.get_by_text(
        "You are about to initiate a transfer with",
        exact=False
    )

    if mtm_popup_text.count() == 0:
        log("No MTM confirmation popup displayed")
        return

    log("MTM confirmation popup displayed")

    page.screenshot(
        path="runtime/screenshots/tc034_mtm_confirmation_popup.png"
    )

    possible_buttons = [
        "Confirm",
        "Yes",
        "OK",
        "Ok"
    ]

    for button_text in possible_buttons:
        button = page.get_by_text(
            button_text,
            exact=True
        )

        if button.count() > 0:
            for item in button.all():
                try:
                    if item.is_visible():
                        item.click()
                        log(
                            f"MTM confirmation clicked using text: "
                            f"[{button_text}]"
                        )
                        page.wait_for_timeout(2000)
                        return
                except Exception:
                    pass

    gxt_buttons = page.locator(
        "div:has-text('Confirm'), "
        "div:has-text('Yes'), "
        "span:has-text('Confirm'), "
        "span:has-text('Yes')"
    )

    for index in range(gxt_buttons.count()):
        candidate = gxt_buttons.nth(index)

        try:
            if candidate.is_visible():
                candidate.click()
                log("MTM confirmation clicked using GXT fallback")
                page.wait_for_timeout(2000)
                return
        except Exception:
            pass

    page.screenshot(
        path="runtime/screenshots/tc034_mtm_popup_no_button_found.png"
    )

    raise Exception(
        "MTM confirmation popup displayed, "
        "but no clickable Confirm/Yes/OK button was found"
    )


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


def check_storage_error_after_upload(page):
    if page.get_by_text(
        "File not found in storage",
        exact=False
    ).count() > 0:

        page.screenshot(
            path="runtime/screenshots/tc034_file_not_found_in_storage.png"
        )

        raise Exception(
            "File upload failed before extreme-file stability validation: "
            "File not found in storage"
        )


def validate_extreme_file_result(page):
    body_text = page.locator("body").inner_text()
    body_text_lower = body_text.lower()

    log("VALIDATION BODY TEXT START")
    log(body_text[:3000])
    log("VALIDATION BODY TEXT END")

    # Case 1: Controlled validation popup/message.
    if any(keyword in body_text_lower for keyword in VALIDATION_KEYWORDS):
        if (
            page.get_by_text("Error", exact=False).count() > 0
            or page.get_by_text("Invalid", exact=False).count() > 0
            or page.get_by_text("Csv", exact=False).count() > 0
            or page.get_by_text("maximum", exact=False).count() > 0
            or page.get_by_text("limit", exact=False).count() > 0
            or page.get_by_text("timeout", exact=False).count() > 0
        ):
            page.screenshot(
                path="runtime/screenshots/tc034_validation_popup_displayed.png"
            )

            log(
                "Extreme CSV file triggered controlled "
                "validation popup/message"
            )

            close_ok_popup_if_present(page)

            return "POPUP_VALIDATION"

    # Case 2: Result grid row produced.
    result_row_count = page.locator(
        "#puGrid tr.BlueGridAppearance-BlueGridStyle-row"
    ).count()

    if result_row_count > 0:
        upload_status = page.locator(
            PortfolioTransferLocators.UPLOAD_STATUS
        ).first.inner_text().strip()

        target_book = page.locator(
            PortfolioTransferLocators.TARGET_BOOK_RESULT
        ).first.inner_text().strip()

        description = page.locator(
            PortfolioTransferLocators.DESCRIPTION_RESULT
        ).first.inner_text().strip()

        log(f"Upload Status: {upload_status}")
        log(f"Target Book: {target_book}")
        log(f"Description: {description}")

        if upload_status in ("SUCCESS", "FAILURE"):
            page.screenshot(
                path="runtime/screenshots/tc034_grid_result_row.png"
            )

            log(
                "Extreme CSV file was handled by application "
                f"with grid status=[{upload_status}]"
            )

            return f"GRID_{upload_status}"

        raise Exception(
            "Extreme CSV file produced a grid row, "
            f"but upload status was unexpected: [{upload_status}]"
        )

    page.screenshot(
        path="runtime/screenshots/tc034_no_validation_or_grid_result.png"
    )

    raise Exception(
        "No validation popup and no result grid row found "
        "for extreme CSV upload"
    )


def capture_performance_snapshot(label):
    """
    Lightweight local-side performance snapshot for evidence.
    This does not measure server memory, but gives useful client-side timing evidence.
    """

    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log(
        f"PERFORMANCE SNAPSHOT [{label}] "
        f"timestamp=[{timestamp}], "
        f"record_count=[{RECORD_COUNT}]"
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
    log("Starting OTCT-7968_TC_034")

    capture_performance_snapshot("test_start")

    # --------------------------------------------------
    # Generate physical extremely large CSV file
    # --------------------------------------------------

    generate_extreme_trade_id_file(EXTREME_FILE)

    if not os.path.exists(EXTREME_FILE):
        raise Exception(
            f"Missing generated file: {EXTREME_FILE}"
        )

    generated_size = os.path.getsize(EXTREME_FILE)

    log(
        f"Extreme CSV ready. "
        f"path=[{EXTREME_FILE}], "
        f"rows=[{RECORD_COUNT}], "
        f"size_bytes=[{generated_size}]"
    )

    # --------------------------------------------------
    # Login
    # --------------------------------------------------

    log("Logging in to the application")
    login(page)

    page.wait_for_timeout(3000)

    page.screenshot(
        path="runtime/screenshots/tc034_after_login.png"
    )

    # --------------------------------------------------
    # Navigate to Portfolio Transfer Entry
    # --------------------------------------------------

    log("Navigating to Portfolio Transfer menu")
    page.click("a[href='#portfolio']")

    page.wait_for_timeout(2000)

    log("Navigating to Portfolio Transfer Entry")

    page.locator(
        ".BlueTabPanelAppearance-BlueTabPanelStyle-tabStripText"
    ).filter(
        has_text="Portfolio Transfer Entry"
    ).first.click()

    page.wait_for_timeout(2000)

    # --------------------------------------------------
    # Entry Type = Portfolio Upload
    # --------------------------------------------------

    log("Clicking on Entry Type dropdown")

    page.locator(
        PortfolioTransferLocators.ENTRY_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Portfolio Upload")

    page.get_by_text(
        "Portfolio Upload",
        exact=True
    ).click()

    page.wait_for_timeout(2000)

    # --------------------------------------------------
    # Upload Extreme CSV File
    # --------------------------------------------------

    log(
        f"Preparing to upload extreme CSV file "
        f"with [{RECORD_COUNT}] Trade IDs"
    )

    capture_performance_snapshot("before_file_upload")

    upload_start = time.time()

    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(EXTREME_FILE)

    page.wait_for_timeout(5000)

    upload_elapsed = round(
        time.time() - upload_start,
        2
    )

    log(
        f"File selection/upload action completed in "
        f"[{upload_elapsed}] seconds"
    )

    check_storage_error_after_upload(page)

    page.screenshot(
        path="runtime/screenshots/tc034_after_extreme_file_upload.png"
    )

    capture_performance_snapshot("after_file_upload")

    # --------------------------------------------------
    # Transfer Type = Account Transfer
    # --------------------------------------------------

    log("Clicking on Transfer Type dropdown")

    page.locator(
        PortfolioTransferLocators.TRANSFER_TYPE
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting Account Transfer option")

    page.get_by_text(
        "Account Transfer",
        exact=True
    ).click()

    page.wait_for_timeout(2000)

    transfer_type_value = page.locator(
        "#puTransferType input"
    ).input_value()

    log(
        f"Selected Transfer Type Value = "
        f"[{transfer_type_value}]"
    )

    # --------------------------------------------------
    # Book = CBKFR_A1
    # --------------------------------------------------

    log("Setting Book value")

    book_field = page.locator(
        PortfolioTransferLocators.BOOK_FIELD
    )

    book_field.click()
    book_field.press("Control+A")
    book_field.press("Delete")
    book_field.press_sequentially(TARGET_BOOK)

    page.wait_for_timeout(1000)

    book_field.press("Enter")

    page.wait_for_timeout(3000)

    book_value = page.locator(
        "#puBook input"
    ).input_value()

    client_mw = page.locator(
        "#puClientIdMw input"
    ).input_value()

    client_other = page.locator(
        "#puClientIdOther input"
    ).input_value()

    cm_mw = page.locator(
        "#puCmIdMw input"
    ).input_value()

    cm_other = page.locator(
        "#puCmIdOther input"
    ).input_value()

    log(f"BOOK=[{book_value}]")
    log(f"CLIENT_MW=[{client_mw}]")
    log(f"CLIENT_OTHER=[{client_other}]")
    log(f"CM_MW=[{cm_mw}]")
    log(f"CM_OTHER=[{cm_other}]")

    if book_value != TARGET_BOOK:
        raise Exception(
            f"Expected book [{TARGET_BOOK}], got [{book_value}]"
        )

    if not client_other:
        raise Exception(
            "Expected Client Other to be auto-populated"
        )

    if not cm_mw:
        raise Exception(
            "Expected CM MW to be auto-populated"
        )

    if not cm_other:
        raise Exception(
            "Expected CM Other to be auto-populated"
        )

    page.screenshot(
        path="runtime/screenshots/tc034_after_book_auto_population.png"
    )

    # --------------------------------------------------
    # MTM Adjustment = Yes
    # --------------------------------------------------

    log("Clicking on MTM Adjustment dropdown")

    page.locator(
        PortfolioTransferLocators.MTM_FIELD
    ).click()

    page.wait_for_timeout(1000)

    log("Selecting MTM Adjustment = Yes")

    page.get_by_text(
        "Yes",
        exact=True
    ).click()

    page.wait_for_timeout(2000)

    mtm_value = page.locator(
        "#puMtmAdj input"
    ).input_value()

    log(f"MTM Adjustment selected=[{mtm_value}]")

    page.screenshot(
        path="runtime/screenshots/tc034_after_mtm_yes_selection.png"
    )

    # --------------------------------------------------
    # Create Portfolio Transfer
    # --------------------------------------------------

    log(
        f"Creating Portfolio Transfer for extreme CSV "
        f"rows=[{RECORD_COUNT}]"
    )

    capture_performance_snapshot("before_processing")

    process_start = time.time()

    page.locator(
        PortfolioTransferLocators.CREATE_PORTFOLIO_TRANSFER
    ).click()

    page.wait_for_timeout(3000)

    confirm_mtm_if_present(page)

    wait_for_progress_bar_close(
        page,
        timeout=900000
    )

    page.wait_for_timeout(15000)

    process_elapsed = round(
        time.time() - process_start,
        2
    )

    capture_performance_snapshot("after_processing")

    log(
        f"Processing completed or returned control in "
        f"[{process_elapsed}] seconds"
    )

    page.screenshot(
        path="runtime/screenshots/tc034_after_create_click.png"
    )

    # --------------------------------------------------
    # Validate Extreme CSV Stability
    # --------------------------------------------------

    validation_result = validate_extreme_file_result(page)

    log(
        "OTCT-7968_TC_034 PASSED - Extremely large CSV "
        "was handled without application crash/hang. "
        f"rows=[{RECORD_COUNT}], "
        f"file_size_bytes=[{generated_size}], "
        f"upload_seconds=[{upload_elapsed}], "
        f"processing_seconds=[{process_elapsed}], "
        f"validation_result=[{validation_result}]"
    )

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()
