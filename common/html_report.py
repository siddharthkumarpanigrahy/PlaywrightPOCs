import base64
import html
import json
import os
from datetime import datetime


SCREENSHOT_ROOT = "runtime/screenshots"
REPORT_DIR = "runtime/reports"
RESULTS_JSON = "runtime/reports/runner_results.json"
REPORT_FILE = "runtime/reports/screenshot_report.html"


def load_results():
    if not os.path.exists(RESULTS_JSON):
        return {}

    with open(RESULTS_JSON, "r", encoding="utf-8") as result_file:
        data = json.load(result_file)

    result_map = {}

    for result in data.get("results", []):
        key = (
            result.get("application", ""),
            result.get("id", "")
        )

        result_map[key] = result

    return result_map


def display_application(application):
    if application == "OTC_GUI":
        return "OTC-GUI"

    if application == "MC_GUI":
        return "MC-GUI"

    return application


def readable_name_from_module(module_path):
    if not module_path:
        return "Functional Validation"

    last_part = module_path.split(".")[-1]

    return (
        last_part
        .replace("otct_7968_", "")
        .replace("tc", "TC ")
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )


def infer_module_from_result(result):
    pack = result.get("pack", "").upper()
    module_path = result.get("module", "").lower()

    if pack == "SMOKE":
        return "Smoke Test"

    if "password" in module_path:
        return "Password Reset Functionality"

    if "mc_gui.security" in module_path:
        return "Input File Validation"

    if "otc_gui.security" in module_path:
        return "Security Validation"

    return "Functional Validation"


def infer_test_name_from_result(application, test_case_id, result):
    module_path = result.get("module", "")

    if test_case_id == "OTC_SMOKE_TC001":
        return "Smoke Test: Login and Logout"

    return readable_name_from_module(module_path)


def extract_tc_number(file_name):
    lower_name = file_name.lower()

    if lower_name.startswith("mc_tc"):
        parts = lower_name.split("_")
        if len(parts) >= 2:
            return parts[1].replace("tc", "").zfill(3)

    if lower_name.startswith("tc"):
        parts = lower_name.split("_")
        if parts:
            return parts[0].replace("tc", "").zfill(3)

    return "000"


def infer_screenshot_metadata(file_name):
    lower_name = file_name.lower()

    # OTC smoke screenshots
    if (
        lower_name.startswith("login_logout")
        or lower_name.startswith("otc_login")
        or lower_name.startswith("otc_credentials")
        or lower_name.startswith("otc_after_login")
        or lower_name.startswith("otc_after_logout")
        or "login_logout_success" in lower_name
        or "login_logout_failed" in lower_name
    ):
        return (
            "OTC_GUI",
            "OTC_SMOKE_TC001",
            "Smoke Test: Login and Logout"
        )

    # MC-GUI screenshots
    if lower_name.startswith("mc_tc"):
        tc_number = extract_tc_number(file_name)
        return (
            "MC_GUI",
            f"OTCT-7968_TC_{tc_number}",
            f"MC-GUI TC {tc_number}"
        )

    # OTC-GUI security screenshots
    if lower_name.startswith("tc"):
        tc_number = extract_tc_number(file_name)
        return (
            "OTC_GUI",
            f"OTCT-7968_TC_{tc_number}",
            f"OTC-GUI TC {tc_number}"
        )

    # Safe fallback
    return (
        "OTC_GUI",
        "GENERAL_VALIDATION",
        "Functional Validation"
    )


def get_step_name(file_name):
    name_without_extension = os.path.splitext(file_name)[0]
    lower_name = name_without_extension.lower()

    if lower_name.startswith("login_logout_success"):
        return "Login and Logout Success"

    if lower_name.startswith("login_logout_failed"):
        return "Login and Logout Failed"

    if lower_name.startswith("otc_login"):
        return "OTC Login Page"

    if lower_name.startswith("otc_credentials"):
        return "Credentials Entered"

    if lower_name.startswith("otc_after_login"):
        return "After Login"

    if lower_name.startswith("otc_after_logout"):
        return "After Logout"

    if lower_name.startswith("mc_tc"):
        parts = name_without_extension.split("_")
        return " ".join(parts[2:]).replace("-", " ").strip().title()

    if lower_name.startswith("tc"):
        parts = name_without_extension.split("_")
        return " ".join(parts[1:]).replace("-", " ").strip().title()

    return name_without_extension.replace("_", " ").replace("-", " ").title()


def encode_image_base64(path):
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


def collect_screenshots(result_map):
    screenshots = []

    if not os.path.exists(SCREENSHOT_ROOT):
        return screenshots

    for root, _, files in os.walk(SCREENSHOT_ROOT):
        for file_name in files:
            if not file_name.lower().endswith(".png"):
                continue

            absolute_path = os.path.join(root, file_name)

            application, test_case_id, inferred_name = infer_screenshot_metadata(
                file_name
            )

            # Avoid stale screenshots from previous runs.
            # If result_map exists, only keep screenshots for tests in current execution.
            if result_map and (application, test_case_id) not in result_map:
                continue

            screenshots.append(
                {
                    "file_name": file_name,
                    "absolute_path": absolute_path,
                    "application": application,
                    "test_case_id": test_case_id,
                    "inferred_name": inferred_name,
                    "step_name": get_step_name(file_name),
                    "modified_time": os.path.getmtime(absolute_path)
                }
            )

    screenshots.sort(
        key=lambda item: (
            item["application"],
            item["test_case_id"],
            item["modified_time"]
        )
    )

    return screenshots


def build_grouped_from_results(result_map):
    grouped = {}

    for (application, test_case_id), result in result_map.items():
        module = infer_module_from_result(result)

        test_name = infer_test_name_from_result(
            application,
            test_case_id,
            result
        )

        grouped.setdefault(
            application,
            {
                "display": display_application(application),
                "modules": {}
            }
        )

        grouped[application]["modules"].setdefault(
            module,
            {}
        )

        grouped[application]["modules"][module].setdefault(
            test_case_id,
            {
                "name": test_name,
                "screenshots": []
            }
        )

    return grouped

def attach_screenshots_to_grouped(grouped, screenshots):
    for screenshot in screenshots:
        application = screenshot["application"]
        test_case_id = screenshot["test_case_id"]

        attached = False

        if application in grouped:
            for module in grouped[application]["modules"]:
                if test_case_id in grouped[application]["modules"][module]:
                    grouped[application]["modules"][module][test_case_id]["screenshots"].append(
                        screenshot
                    )
                    attached = True
                    break

        if attached:
            continue

        grouped.setdefault(
            application,
            {
                "display": display_application(application),
                "modules": {}
            }
        )

        grouped[application]["modules"].setdefault(
            "Functional Validation",
            {}
        )

        grouped[application]["modules"]["Functional Validation"].setdefault(
            test_case_id,
            {
                "name": screenshot["inferred_name"],
                "screenshots": []
            }
        )

        grouped[application]["modules"]["Functional Validation"][test_case_id]["screenshots"].append(
            screenshot
        )

    return grouped

def get_status(result_map, application, test_case_id):
    result = result_map.get(
        (
            application,
            test_case_id
        )
    )

    if not result:
        return "NOT RUN"

    return result.get("status", "UNKNOWN")


def get_duration(result_map, application, test_case_id):
    result = result_map.get(
        (
            application,
            test_case_id
        )
    )

    if not result:
        return ""

    duration = result.get("duration_seconds")

    if duration is None:
        return ""

    return f"{duration}s"


def status_class(status):
    status = status.upper()

    if status == "PASSED":
        return "status-passed"

    if status == "FAILED":
        return "status-failed"

    return "status-not-run"


INLINE_CSS = """
:root {
    --primary: #155eef;
    --primary-dark: #0b4dbb;
    --primary-light: #eef4ff;
    --success-bg: #dcfae6;
    --success-text: #067647;
    --success-border: #abefc6;
    --failure-bg: #fee4e2;
    --failure-text: #b42318;
    --failure-border: #fecdca;
    --neutral-bg: #f2f4f7;
    --neutral-text: #344054;
    --neutral-border: #d0d5dd;
    """
def generate_html_report():
    result_map = load_results()

    grouped = build_grouped_from_results(
        result_map
    )

    screenshots = collect_screenshots(
        result_map
    )

    grouped = attach_screenshots_to_grouped(
        grouped,
        screenshots
    )

    return write_html( # type: ignore
        grouped,
        result_map,
        len(screenshots)
    )


if __name__ == "__main__":
    report_path = generate_html_report()
    print(f"Generated HTML report: {report_path}")