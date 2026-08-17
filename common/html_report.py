import os
import html
from datetime import datetime


SCREENSHOT_ROOT = "runtime/screenshots"
REPORT_DIR = "runtime/reports"
REPORT_FILE = "runtime/reports/screenshot_report.html"


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
        "name": "Duplicate Trade IDs with spaces"
    },
    "013": {
        "id": "OTCT-7968_TC_013",
        "module": "Password Reset Functionality",
        "name": "Password field masking"
    },
    "014": {
        "id": "OTCT-7968_TC_014",
        "module": "Password Reset Functionality",
        "name": "Password confirm mismatch"
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


def extract_tc_number(file_name):
    lower_name = file_name.lower()

    if lower_name.startswith("mc_tc"):
        prefix = lower_name.split("_")[1]
        return prefix.replace("tc", "").zfill(3)

    if lower_name.startswith("tc"):
        prefix = lower_name.split("_")[0]
        return prefix.replace("tc", "").zfill(3)

    return "000"


def infer_application(file_name):
    lower_name = file_name.lower()

    if lower_name.startswith("mc_tc"):
        return "MC-GUI"

    return "OTC-GUI"


def infer_metadata(file_name):
    application = infer_application(file_name)
    tc_number = extract_tc_number(file_name)

    if application == "MC-GUI":
        metadata = MC_TEST_METADATA.get(
            tc_number,
            {
                "id": f"OTCT-7968_TC_{tc_number}",
                "module": "Unmapped",
                "name": "Unmapped MC-GUI Test"
            }
        )
    else:
        metadata = OTC_TEST_METADATA.get(
            tc_number,
            {
                "id": f"OTCT-7968_TC_{tc_number}",
                "module": "Unmapped",
                "name": "Unmapped OTC-GUI Test"
            }
        )

    return application, metadata["module"], metadata["id"], metadata["name"]


def get_step_name(file_name):
    name_without_extension = os.path.splitext(file_name)[0]

    lower_name = name_without_extension.lower()

    if lower_name.startswith("mc_tc"):
        parts = name_without_extension.split("_")
        return "_".join(parts[2:]) if len(parts) > 2 else name_without_extension

    if lower_name.startswith("tc"):
        parts = name_without_extension.split("_")
        return "_".join(parts[1:]) if len(parts) > 1 else name_without_extension

    return name_without_extension


def collect_screenshots():
    screenshots = []

    if not os.path.exists(SCREENSHOT_ROOT):
        return screenshots

    for root, _, files in os.walk(SCREENSHOT_ROOT):
        for file_name in files:
            if not file_name.lower().endswith(".png"):
                continue

            absolute_path = os.path.join(root, file_name)

            relative_path = os.path.relpath(
                absolute_path,
                REPORT_DIR
            ).replace("\\", "/")

            application, module, test_case_id, test_case_name = infer_metadata(
                file_name
            )

            screenshots.append(
                {
                    "file_name": file_name,
                    "absolute_path": absolute_path,
                    "relative_path": relative_path,
                    "application": application,
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


def group_screenshots(screenshots):
    grouped = {}

    for screenshot in screenshots:
        application = screenshot["application"]
        module = screenshot["module"]
        test_case_id = screenshot["test_case_id"]

        grouped.setdefault(application, {})
        grouped[application].setdefault(module, {})
        grouped[application][module].setdefault(test_case_id, {
            "name": screenshot["test_case_name"],
            "screenshots": []
        })

        grouped[application][module][test_case_id]["screenshots"].append(
            screenshot
        )

    return grouped


def write_html(grouped, total_screenshots):
    os.makedirs(REPORT_DIR, exist_ok=True)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_parts = []

    html_parts.append(
        """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Playwright UI Automation Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 24px;
            background: #f6f8fa;
            color: #24292f;
        }

        h1 {
            color: #0b5cab;
            margin-bottom: 4px;
        }

        h2 {
            margin: 0;
        }

        h3 {
            margin-bottom: 8px;
        }

        h4 {
            margin-bottom: 4px;
        }

        .summary {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 16px 0 24px 0;
        }

        .application {
            margin-top: 28px;
            padding: 14px 18px;
            background: #eaf3ff;
            border-left: 6px solid #0969da;
            border-radius: 8px;
        }

        .module {
            margin-top: 18px;
            padding: 14px;
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
        }

        .testcase {
            margin-top: 14px;
            padding: 12px;
            background: #fafafa;
            border: 1px solid #eaeef2;
            border-radius: 8px;
        }

        .testcase-name {
            color: #57606a;
            font-size: 13px;
            margin-bottom: 10px;
        }

        .badge {
            display: inline-block;
            background: #0969da;
            color: #ffffff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 8px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 14px;
            margin-top: 10px;
        }

        .card {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }

        .card img {
            width: 100%;
            max-height: 260px;
            object-fit: contain;
            border: 1px solid #d8dee4;
            background: #ffffff;
            border-radius: 4px;
        }

        .step {
            font-size: 13px;
            font-weight: bold;
            margin-top: 8px;
            color: #24292f;
            word-break: break-word;
        }

        .filename {
            font-size: 12px;
            color: #57606a;
            word-break: break-all;
            margin-top: 4px;
        }

        .empty {
            background: #fff8c5;
            border: 1px solid #f0d98c;
            border-radius: 8px;
            padding: 16px;
        }

        a {
            color: #0969da;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
        """
    )

    html_parts.append("<h1>OTCT-7968 Screenshot Report</h1>")

    html_parts.append(
        f"""
<div class="summary">
    <div><strong>Generated At:</strong> {html.escape(generated_at)}</div>
    <div><strong>Total Screenshots:</strong> {total_screenshots}</div>
</div>
        """
    )

    if total_screenshots == 0:
        html_parts.append(
            """
<div class="empty">
    No screenshots were found under runtime/screenshots.
</div>
            """
        )
    else:
        for application, modules in grouped.items():
            html_parts.append(
                f"""
<div class="application">
    <h2>{html.escape(application)}</h2>
</div>
                """
            )

            for module, test_cases in modules.items():
                module_count = sum(
                    len(test_case_data["screenshots"])
                    for test_case_data in test_cases.values()
                )

                html_parts.append(
                    f"""
<div class="module">
    <h3>{html.escape(module)} <span class="badge">{module_count}</span></h3>
                    """
                )

                for test_case_id, test_case_data in test_cases.items():
                    screenshots = test_case_data["screenshots"]
                    test_case_name = test_case_data["name"]

                    html_parts.append(
                        f"""
<div class="testcase">
    <h4>{html.escape(test_case_id)} <span class="badge">{len(screenshots)}</span></h4>
    <div class="testcase-name">{html.escape(test_case_name)}</div>
    <div class="grid">
                        """
                    )

                    for screenshot in screenshots:
                        relative_path = html.escape(screenshot["relative_path"])
                        file_name = html.escape(screenshot["file_name"])
                        step_name = html.escape(screenshot["step_name"])

                        html_parts.append(
                            f"""
        <div class="card">
            {relative_path}
                {relative_path}
            </a>
            <div class="step">{step_name}</div>
            <div class="filename">{file_name}</div>
        </div>
                            """
                        )

                    html_parts.append(
                        """
    </div>
</div>
                        """
                    )

                html_parts.append("</div>")

    html_parts.append(
        """
</body>
</html>
        """
    )

    with open(REPORT_FILE, "w", encoding="utf-8") as report:
        report.write("\n".join(html_parts))

    return REPORT_FILE


def generate_html_report():
    screenshots = collect_screenshots()
    grouped = group_screenshots(screenshots)

    return write_html(
        grouped,
        len(screenshots)
    )


if __name__ == "__main__":
    report = generate_html_report()
    print(f"Generated screenshot report: {report}")
