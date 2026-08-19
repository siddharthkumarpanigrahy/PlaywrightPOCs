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

    html_parts.append(
        """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Playwright Execution Report</title>
    <style>
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
            --warning-bg: #fffaeb;
            --warning-border: #fedf89;
            --warning-text: #93370d;
            --page-bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #101828;
            --text-muted: #667085;
            --border: #d0d5dd;
            --soft-border: #eaecf0;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: var(--page-bg);
            color: var(--text-main);
        }

        .page {
            padding: 28px;
        }

        .header {
            background: linear-gradient(90deg, var(--primary-dark), var(--primary));
            color: #ffffff;
            border-radius: 16px;
            padding: 26px 30px;
            margin-bottom: 22px;
            box-shadow: 0 4px 12px rgba(21, 94, 239, 0.18);
        }

        .header h1 {
            margin: 0;
            font-size: 30px;
            font-weight: 800;
        }

        .header .sub {
            margin-top: 8px;
            font-size: 14px;
            opacity: 0.9;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }

        .summary-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.08);
        }

        .summary-label {
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 600;
        }

        .summary-value {
            margin-top: 8px;
            font-size: 28px;
            font-weight: 800;
        }

        .summary-pass {
            color: var(--success-text);
        }

        .summary-fail {
            color: var(--failure-text);
        }

        .summary-neutral {
            color: var(--neutral-text);
        }

        .application-title {
            background: var(--primary-light);
            border-left: 6px solid var(--primary);
            border-radius: 12px;
            padding: 15px 18px;
            font-size: 22px;
            font-weight: 800;
            margin-top: 24px;
            margin-bottom: 16px;
        }

        .module-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
        }

        .module-title {
            font-size: 18px;
            font-weight: 800;
            margin-bottom: 14px;
        }

        .test-card {
            border: 1px solid var(--soft-border);
            background: #fcfcfd;
            border-radius: 14px;
            padding: 15px;
            margin-top: 14px;
        }

        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 12px;
        }

        .test-id {
            font-weight: 800;
            font-size: 15px;
        }

        .test-name {
            margin-top: 4px;
            color: var(--text-muted);
            font-size: 13px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 800;
            white-space: nowrap;
            margin-left: 6px;
        }

        .status-passed {
            background: var(--success-bg);
            color: var(--success-text);
            border: 1px solid var(--success-border);
        }

        .status-failed {
            background: var(--failure-bg);
            color: var(--failure-text);
            border: 1px solid var(--failure-border);
        }

        .status-not-run {
            background: var(--neutral-bg);
            color: var(--neutral-text);
            border: 1px solid var(--neutral-border);
        }

        .count-badge {
            background: var(--primary-light);
            color: var(--primary);
            border: 1px solid #c7d7fe;
        }

        .duration-badge {
            background: #f9fafb;
            color: #475467;
            border: 1px solid var(--neutral-border);
        }

        details {
            margin-top: 10px;
        }

        summary {
            cursor: pointer;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 10px;
        }

        .screenshot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 14px;
        }

        .shot-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
        }

        .shot-card img {
            width: 100%;
            height: 230px;
            object-fit: contain;
            background: #f2f4f7;
            border-bottom: 1px solid var(--soft-border);
            display: block;
        }

        .shot-body {
            padding: 10px 12px;
        }

        .step-name {
            font-weight: 800;
            font-size: 13px;
            color: #1d2939;
            margin-bottom: 4px;
            word-break: break-word;
        }

        .file-name {
            color: var(--text-muted);
            font-size: 12px;
            word-break: break-all;
        }

        .no-screenshots {
            background: var(--warning-bg);
            border: 1px solid var(--warning-border);
            color: var(--warning-text);
            border-radius: 12px;
            padding: 14px;
            font-weight: 600;
        }

        .empty {
            background: var(--warning-bg);
            border: 1px solid var(--warning-border);
            border-radius: 12px;
            padding: 18px;
            color: var(--warning-text);
        }

        .footer {
            margin-top: 26px;
            color: var(--text-muted);
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="page">
        """
    )

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
                {safe_image_src}">
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
