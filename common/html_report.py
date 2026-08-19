import html
import json
import os
from datetime import datetime


SCREENSHOT_ROOT = "runtime/screenshots"
REPORT_DIR = "runtime/reports"
RESULTS_JSON = "runtime/reports/runner_results.json"
REPORT_FILE = "runtime/reports/screenshot_report.html"


# --------------------------------------------------
# Metadata
# --------------------------------------------------

OTC_TEST_METADATA = {
    "001": {
        "id": "OTCT-7968_TC_001",
        "module": "Input File Validation",
        "name": "Long filename"
    },
    "002": {
        "id": "OTCT-7968_TC_002",
        "module": "Input File Validation",
        "name": "Filename with leading/trailing spaces"
    },
    "003": {
        "id": "OTCT-7968_TC_003",
        "module": "Input File Validation",
        "name": "Empty file"
    },
    "004": {
        "id": "OTCT-7968_TC_004",
        "module": "Input File Validation",
        "name": "Missing header"
    },
    "005": {
        "id": "OTCT-7968_TC_005",
        "module": "Input File Validation",
        "name": "Extra columns"
    },
    "006": {
        "id": "OTCT-7968_TC_006",
        "module": "Input File Validation",
        "name": "Special characters"
    },
    "007": {
        "id": "OTCT-7968_TC_007",
        "module": "Input File Validation",
        "name": "Unicode and emoji"
    },
    "008": {
        "id": "OTCT-7968_TC_008",
        "module": "Input File Validation",
        "name": "Formula injection"
    },
    "009": {
        "id": "OTCT-7968_TC_009",
        "module": "Input File Validation",
        "name": "Hyperlinks and embedded objects"
    },
    "010": {
        "id": "OTCT-7968_TC_010",
        "module": "Transaction Authorization",
        "name": "Unauthorized upload restriction"
    },
    "011": {
        "id": "OTCT-7968_TC_011",
        "module": "Transaction Authorization",
        "name": "Read-only upload restriction"
    },
    "012": {
        "id": "OTCT-7968_TC_012",
        "module": "Duplicate Record Injection",
        "name": "Duplicate Trade IDs with leading/trailing spaces"
    },
    "013": {
        "id": "OTCT-7968_TC_013",
        "module": "Password Reset Functionality",
        "name": "Password field masking"
    },
    "014": {
        "id": "OTCT-7968_TC_014",
        "module": "Password Reset Functionality",
        "name": "Password and confirm password mismatch"
    },
    "015": {
        "id": "OTCT-7968_TC_015",
        "module": "Password Reset Functionality",
        "name": "Password complexity"
    },
    "016": {
        "id": "OTCT-7968_TC_016",
        "module": "Password Reset Functionality",
        "name": "Password Reset button visible"
    },
    "017": {
        "id": "OTCT-7968_TC_017",
        "module": "Password Reset Functionality",
        "name": "Password Reset button hidden"
    },
    "018": {
        "id": "OTCT-7968_TC_018",
        "module": "Maximum Record Limit",
        "name": "50,000 Trade IDs"
    },
    "019": {
        "id": "OTCT-7968_TC_019",
        "module": "Maximum Record Limit",
        "name": "49,999 Trade IDs"
    },
    "020": {
        "id": "OTCT-7968_TC_020",
        "module": "Maximum Record Limit",
        "name": "Extremely large CSV stability"
    },
    "021": {
        "id": "OTCT-7968_TC_021",
        "module": "Password Reset Functionality",
        "name": "Generated password policy"
    },
    "022": {
        "id": "OTCT-7968_TC_022",
        "module": "Password Reset Functionality",
        "name": "Password reset same member"
    },
    "023": {
        "id": "OTCT-7968_TC_023",
        "module": "Password Reset Functionality",
        "name": "Password reset different member"
    },
    "024": {
        "id": "OTCT-7968_TC_024",
        "module": "Password Reset Functionality",
        "name": "Password reset REM user"
    }
}


MC_TEST_METADATA = {
    "001": {
        "id": "OTCT-7968_TC_001",
        "module": "Input File Validation",
        "name": "Long filename"
    },
    "002": {
        "id": "OTCT-7968_TC_002",
        "module": "Input File Validation",
        "name": "Filename with leading/trailing spaces"
    },
    "003": {
        "id": "OTCT-7968_TC_003",
        "module": "Input File Validation",
        "name": "Empty file"
    },
    "004": {
        "id": "OTCT-7968_TC_004",
        "module": "Input File Validation",
        "name": "Missing header"
    },
    "005": {
        "id": "OTCT-7968_TC_005",
        "module": "Input File Validation",
        "name": "Extra columns"
    },
    "006": {
        "id": "OTCT-7968_TC_006",
        "module": "Input File Validation",
        "name": "Special characters"
    },
    "007": {
        "id": "OTCT-7968_TC_007",
        "module": "Input File Validation",
        "name": "Unicode and emoji"
    },
    "008": {
        "id": "OTCT-7968_TC_008",
        "module": "Input File Validation",
        "name": "Formula injection"
    },
    "009": {
        "id": "OTCT-7968_TC_009",
        "module": "Input File Validation",
        "name": "Hyperlinks and embedded objects"
    }
}


# --------------------------------------------------
# Result Loading
# --------------------------------------------------

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


# --------------------------------------------------
# Inference Helpers
# --------------------------------------------------

def display_application(application):
    if application == "OTC_GUI":
        return "OTC-GUI"

    if application == "MC_GUI":
        return "MC-GUI"

    return application


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


def infer_application(file_name):
    lower_name = file_name.lower()

    if lower_name.startswith("mc_tc"):
        return "MC_GUI"

    return "OTC_GUI"


def infer_metadata(file_name):
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
            "Smoke Test",
            "OTC_SMOKE_TC001",
            "Smoke Test: Login and Logout"
        )

    application = infer_application(file_name)
    tc_number = extract_tc_number(file_name)

    if application == "MC_GUI":
        metadata = MC_TEST_METADATA.get(
            tc_number,
            {
                "id": f"MC_TEST_TC_{tc_number}",
                "module": "General Validation",
                "name": f"MC-GUI Functional Validation TC {tc_number}"
            }
        )
    else:
        metadata = OTC_TEST_METADATA.get(
            tc_number,
            {
                "id": f"OTC_TEST_TC_{tc_number}",
                "module": "General Validation",
                "name": f"OTC-GUI Functional Validation TC {tc_number}"
            }
        )

    return application, metadata["module"], metadata["id"], metadata["name"]


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

    return "General Validation"


def infer_test_name_from_result(application, test_case_id, result):
    module_path = result.get("module", "")

    if test_case_id == "OTC_SMOKE_TC001":
        return "Smoke Test: Login and Logout"

    if application == "MC_GUI":
        for metadata in MC_TEST_METADATA.values():
            if metadata["id"] == test_case_id:
                return metadata["name"]

    if application == "OTC_GUI":
        for metadata in OTC_TEST_METADATA.values():
            if metadata["id"] == test_case_id:
                return metadata["name"]

    module_name = module_path.split(".")[-1]
    module_name = module_name.replace("_", " ").replace("-", " ").title()

    return module_name or test_case_id


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


def status_class(status):
    status = status.upper()

    if status == "PASSED":
        return "status-passed"

    if status == "FAILED":
        return "status-failed"

    if status == "TIMEOUT":
        return "status-failed"

    return "status-not-run"


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


# --------------------------------------------------
# Screenshot Collection
# --------------------------------------------------

def collect_screenshots():
    screenshots = []

    if not os.path.exists(SCREENSHOT_ROOT):
        return screenshots

    for root, _, files in os.walk(SCREENSHOT_ROOT):
        for file_name in files:
            if not file_name.lower().endswith(".png"):
                continue

            absolute_path = os.path.join(root, file_name)

            application, module, test_case_id, test_case_name = infer_metadata(
                file_name
            )

            screenshots.append(
                {
                    "file_name": file_name,
                    "absolute_path": absolute_path,
                    "application": application,
                    "application_display": display_application(application),
                    "module": module,
                    "test_case_id": test_case_id,
                    "test_case_name": test_case_name,
                    "step_name": get_step_name(file_name),
                    "modified_time": os.path.getmtime(absolute_path)
                }
            )

    screenshots.sort(
        key=lambda item: (
            item["application"],
            item["module"],
            item["test_case_id"],
            item["modified_time"]
        )
    )

    return screenshots


# --------------------------------------------------
# Grouping
# --------------------------------------------------

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
                "display": screenshot["application_display"],
                "modules": {}
            }
        )

        grouped[application]["modules"].setdefault(
            screenshot["module"],
            {}
        )

        grouped[application]["modules"][screenshot["module"]].setdefault(
            test_case_id,
            {
                "name": screenshot["test_case_name"],
                "screenshots": []
            }
        )

        grouped[application]["modules"][screenshot["module"]][test_case_id]["screenshots"].append(
            screenshot
        )

    return grouped


# --------------------------------------------------
# HTML Writer
# --------------------------------------------------

def write_html(grouped, result_map, total_screenshots):
    os.makedirs(REPORT_DIR, exist_ok=True)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    not_run_tests = 0

    for application, app_data in grouped.items():
        for _, test_cases in app_data["modules"].items():
            for test_case_id in test_cases:
                total_tests += 1

                status = get_status(
                    result_map,
                    application,
                    test_case_id
                )

                if status == "PASSED":
                    passed_tests += 1
                elif status == "FAILED":
                    failed_tests += 1
                else:
                    not_run_tests += 1

    html_parts = []

    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html>")
    html_parts.append("<head>")
    html_parts.append("    <meta charset=\"utf-8\">")
    html_parts.append("    <title>Playwright Execution Report</title>")
    html_parts.append("    <style>")
    html_parts.append("        :root {")
    html_parts.append("            --primary: #155eef;")
    html_parts.append("            --primary-dark: #0b4dbb;")
    html_parts.append("            --primary-light: #eef4ff;")
    html_parts.append("            --success-bg: #dcfae6;")
    html_parts.append("            --success-text: #067647;")
    html_parts.append("            --success-border: #abefc6;")
    html_parts.append("            --failure-bg: #fee4e2;")
    html_parts.append("            --failure-text: #b42318;")
    html_parts.append("            --failure-border: #fecdca;")
    html_parts.append("            --neutral-bg: #f2f4f7;")
    html_parts.append("            --neutral-text: #344054;")
    html_parts.append("            --neutral-border: #d0d5dd;")
    html_parts.append("            --warning-bg: #fffaeb;")
    html_parts.append("            --warning-border: #fedf89;")
    html_parts.append("            --warning-text: #93370d;")
    html_parts.append("            --page-bg: #f8fafc;")
    html_parts.append("            --card-bg: #ffffff;")
    html_parts.append("            --text-main: #101828;")
    html_parts.append("            --text-muted: #667085;")
    html_parts.append("            --border: #d0d5dd;")
    html_parts.append("            --soft-border: #eaecf0;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        * {")
    html_parts.append("            box-sizing: border-box;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        body {")
    html_parts.append("            margin: 0;")
    html_parts.append("            font-family: \"Segoe UI\", Arial, sans-serif;")
    html_parts.append("            background: var(--page-bg);")
    html_parts.append("            color: var(--text-main);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .page {")
    html_parts.append("            padding: 28px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .header {")
    html_parts.append("            background: linear-gradient(90deg, var(--primary-dark), var(--primary));")
    html_parts.append("            color: #ffffff;")
    html_parts.append("            border-radius: 16px;")
    html_parts.append("            padding: 26px 30px;")
    html_parts.append("            margin-bottom: 22px;")
    html_parts.append("            box-shadow: 0 4px 12px rgba(21, 94, 239, 0.18);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .header h1 {")
    html_parts.append("            margin: 0;")
    html_parts.append("            font-size: 30px;")
    html_parts.append("            font-weight: 800;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .header .sub {")
    html_parts.append("            margin-top: 8px;")
    html_parts.append("            font-size: 14px;")
    html_parts.append("            opacity: 0.9;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-grid {")
    html_parts.append("            display: grid;")
    html_parts.append("            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));")
    html_parts.append("            gap: 14px;")
    html_parts.append("            margin-bottom: 24px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-card {")
    html_parts.append("            background: var(--card-bg);")
    html_parts.append("            border: 1px solid var(--border);")
    html_parts.append("            border-radius: 14px;")
    html_parts.append("            padding: 16px 18px;")
    html_parts.append("            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.08);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-label {")
    html_parts.append("            color: var(--text-muted);")
    html_parts.append("            font-size: 13px;")
    html_parts.append("            font-weight: 600;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-value {")
    html_parts.append("            margin-top: 8px;")
    html_parts.append("            font-size: 28px;")
    html_parts.append("            font-weight: 800;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-pass {")
    html_parts.append("            color: var(--success-text);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-fail {")
    html_parts.append("            color: var(--failure-text);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .summary-neutral {")
    html_parts.append("            color: var(--neutral-text);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .application-title {")
    html_parts.append("            background: var(--primary-light);")
    html_parts.append("            border-left: 6px solid var(--primary);")
    html_parts.append("            border-radius: 12px;")
    html_parts.append("            padding: 15px 18px;")
    html_parts.append("            font-size: 22px;")
    html_parts.append("            font-weight: 800;")
    html_parts.append("            margin-top: 24px;")
    html_parts.append("            margin-bottom: 16px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .module-card {")
    html_parts.append("            background: var(--card-bg);")
    html_parts.append("            border: 1px solid var(--border);")
    html_parts.append("            border-radius: 16px;")
    html_parts.append("            padding: 18px;")
    html_parts.append("            margin-bottom: 20px;")
    html_parts.append("            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .module-title {")
    html_parts.append("            font-size: 18px;")
    html_parts.append("            font-weight: 800;")
    html_parts.append("            margin-bottom: 14px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .test-card {")
    html_parts.append("            border: 1px solid var(--soft-border);")
    html_parts.append("            background: #fcfcfd;")
    html_parts.append("            border-radius: 14px;")
    html_parts.append("            padding: 15px;")
    html_parts.append("            margin-top: 14px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .test-header {")
    html_parts.append("            display: flex;")
    html_parts.append("            justify-content: space-between;")
    html_parts.append("            align-items: flex-start;")
    html_parts.append("            gap: 16px;")
    html_parts.append("            margin-bottom: 12px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .test-id {")
    html_parts.append("            font-weight: 800;")
    html_parts.append("            font-size: 15px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .test-name {")
    html_parts.append("            margin-top: 4px;")
    html_parts.append("            color: var(--text-muted);")
    html_parts.append("            font-size: 13px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .badge {")
    html_parts.append("            display: inline-flex;")
    html_parts.append("            align-items: center;")
    html_parts.append("            border-radius: 999px;")
    html_parts.append("            padding: 4px 10px;")
    html_parts.append("            font-size: 12px;")
    html_parts.append("            font-weight: 800;")
    html_parts.append("            white-space: nowrap;")
    html_parts.append("            margin-left: 6px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .status-passed {")
    html_parts.append("            background: var(--success-bg);")
    html_parts.append("            color: var(--success-text);")
    html_parts.append("            border: 1px solid var(--success-border);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .status-failed {")
    html_parts.append("            background: var(--failure-bg);")
    html_parts.append("            color: var(--failure-text);")
    html_parts.append("            border: 1px solid var(--failure-border);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .status-not-run {")
    html_parts.append("            background: var(--neutral-bg);")
    html_parts.append("            color: var(--neutral-text);")
    html_parts.append("            border: 1px solid var(--neutral-border);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .count-badge {")
    html_parts.append("            background: var(--primary-light);")
    html_parts.append("            color: var(--primary);")
    html_parts.append("            border: 1px solid #c7d7fe;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .duration-badge {")
    html_parts.append("            background: #f9fafb;")
    html_parts.append("            color: #475467;")
    html_parts.append("            border: 1px solid var(--neutral-border);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        details {")
    html_parts.append("            margin-top: 10px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        summary {")
    html_parts.append("            cursor: pointer;")
    html_parts.append("            color: var(--primary);")
    html_parts.append("            font-weight: 700;")
    html_parts.append("            margin-bottom: 10px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .screenshot-grid {")
    html_parts.append("            display: grid;")
    html_parts.append("            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));")
    html_parts.append("            gap: 14px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .shot-card {")
    html_parts.append("            background: #ffffff;")
    html_parts.append("            border: 1px solid var(--border);")
    html_parts.append("            border-radius: 14px;")
    html_parts.append("            overflow: hidden;")
    html_parts.append("            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .shot-card img {")
    html_parts.append("            width: 100%;")
    html_parts.append("            height: 230px;")
    html_parts.append("            object-fit: contain;")
    html_parts.append("            background: #f2f4f7;")
    html_parts.append("            border-bottom: 1px solid var(--soft-border);")
    html_parts.append("            display: block;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .shot-body {")
    html_parts.append("            padding: 10px 12px;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .step-name {")
    html_parts.append("            font-weight: 800;")
    html_parts.append("            font-size: 13px;")
    html_parts.append("            color: #1d2939;")
    html_parts.append("            margin-bottom: 4px;")
    html_parts.append("            word-break: break-word;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .file-name {")
    html_parts.append("            color: var(--text-muted);")
    html_parts.append("            font-size: 12px;")
    html_parts.append("            word-break: break-all;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .no-screenshots {")
    html_parts.append("            background: var(--warning-bg);")
    html_parts.append("            border: 1px solid var(--warning-border);")
    html_parts.append("            color: var(--warning-text);")
    html_parts.append("            border-radius: 12px;")
    html_parts.append("            padding: 14px;")
    html_parts.append("            font-weight: 600;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .empty {")
    html_parts.append("            background: var(--warning-bg);")
    html_parts.append("            border: 1px solid var(--warning-border);")
    html_parts.append("            border-radius: 12px;")
    html_parts.append("            padding: 18px;")
    html_parts.append("            color: var(--warning-text);")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        .footer {")
    html_parts.append("            margin-top: 26px;")
    html_parts.append("            color: var(--text-muted);")
    html_parts.append("            font-size: 12px;")
    html_parts.append("            text-align: center;")
    html_parts.append("        }")
    html_parts.append("    </style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append("<div class=\"page\">")

    html_parts.append(
        f"""
<div class="header">
    <h1>Playwright Execution Report</h1>
    <div class="sub">Generated at {html.escape(generated_at)}</div>
</div>

<div class="summary-grid">
    <div class="summary-card">
        <div class="summary-label">Test Cases</div>
        <div class="summary-value">{total_tests}</div>
    </div>
    <div class="summary-card">
        <div class="summary-label">Passed</div>
        <div class="summary-value summary-pass">{passed_tests}</div>
    </div>
    <div class="summary-card">
        <div class="summary-label">Failed</div>
        <div class="summary-value summary-fail">{failed_tests}</div>
    </div>
    <div class="summary-card">
        <div class="summary-label">Not Run / Unknown</div>
        <div class="summary-value summary-neutral">{not_run_tests}</div>
    </div>
    <div class="summary-card">
        <div class="summary-label">Screenshots</div>
        <div class="summary-value">{total_screenshots}</div>
    </div>
</div>
        """
    )

    if total_tests == 0:
        html_parts.append(
            """
<div class="empty">
    No test results found. Check runtime/reports/runner_results.json.
</div>
            """
        )

    for application, app_data in grouped.items():
        html_parts.append(
            f"""
<div class="application-title">{html.escape(app_data["display"])}</div>
            """
        )

        for module, test_cases in app_data["modules"].items():
            module_screenshot_count = sum(
                len(test_data["screenshots"])
                for test_data in test_cases.values()
            )

            html_parts.append(
                f"""
<div class="module-card">
    <div class="module-title">
        {html.escape(module)}
        <span class="badge count-badge">{module_screenshot_count} screenshots</span>
    </div>
                """
            )

            for test_case_id, test_data in test_cases.items():
                status = get_status(
                    result_map,
                    application,
                    test_case_id
                )

                duration = get_duration(
                    result_map,
                    application,
                    test_case_id
                )

                screenshots = test_data["screenshots"]

                html_parts.append(
                    f"""
<div class="test-card">
    <div class="test-header">
        <div>
            <div class="test-id">{html.escape(test_data["name"])}</div>
            <div class="test-name">Reference ID: {html.escape(test_case_id)}</div>
        </div>
        <div>
            <span class="badge {status_class(status)}">{html.escape(status)}</span>
            <span class="badge count-badge">{len(screenshots)} screenshots</span>
            <span class="badge duration-badge">{html.escape(duration)}</span>
        </div>
    </div>

    <details open>
        <summary>View screenshots</summary>
                    """
                )

                if screenshots:
                    html_parts.append('<div class="screenshot-grid">')

                    for screenshot in screenshots:
                        image_src = os.path.relpath(
                            screenshot["absolute_path"],
                            REPORT_DIR
                        ).replace("\\", "/")

                        safe_image_src = html.escape(image_src)
                        safe_file_name = html.escape(screenshot["file_name"])
                        safe_step_name = html.escape(screenshot["step_name"])

                        html_parts.append(
                            f"""
            <div class="shot-card">
                <img src="{safe_image_src}" alt="{safe_step_name}">
                <div class="shot-body">
                    <div class="step-name">{safe_step_name}</div>
                    <div class="file-name">{safe_file_name}</div>
                </div>
            </div>
                            """
                        )

                    html_parts.append("</div>")
                else:
                    html_parts.append(
                        """
        <div class="no-screenshots">
            No screenshots were captured for this test case.
        </div>
                        """
                    )

                html_parts.append(
                    """
    </details>
</div>
                    """
                )

            html_parts.append("</div>")

    html_parts.append(
        """
<div class="footer">
    Generated by Playwright Automation Runner
</div>
</div>
</body>
</html>
        """
    )

    with open(REPORT_FILE, "w", encoding="utf-8") as report:
        report.write("\n".join(html_parts))

    return REPORT_FILE


def generate_html_report():
    result_map = load_results()
    grouped = build_grouped_from_results(result_map)

    screenshots = collect_screenshots()

    grouped = attach_screenshots_to_grouped(
        grouped,
        screenshots
    )

    return write_html(
        grouped,
        result_map,
        len(screenshots)
    )


if __name__ == "__main__":
    report_path = generate_html_report()
    print(f"Generated HTML report: {report_path}")
