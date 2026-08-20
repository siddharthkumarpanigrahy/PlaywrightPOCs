import base64
import html
import json
import mimetypes
import os
import re
from datetime import datetime


SCREENSHOT_ROOT = "runtime/screenshots"
REPORT_DIR = "runtime/reports"
RESULTS_JSON = "runtime/reports/runner_results.json"
REPORT_FILE = "runtime/reports/screenshot_report.html"


TEST_NAMES = {
    "OTC_SMOKE_TC001": "Smoke Test: Login and Logout",
    "OTCT-7968_TC_001": "Validate upload of a file with a long filename",
    "OTCT-7968_TC_002": "Validate filename with leading or trailing spaces",
    "OTCT-7968_TC_003": "Validate upload of an empty file",
    "OTCT-7968_TC_004": "Validate upload of a file with a missing header",
    "OTCT-7968_TC_005": "Validate upload of a file with additional columns",
    "OTCT-7968_TC_006": "Validate special-character handling",
    "OTCT-7968_TC_007": "Validate Unicode and emoji handling",
    "OTCT-7968_TC_008": "Validate CSV formula-injection prevention",
    "OTCT-7968_TC_009": "Validate hyperlinks and embedded-object handling",
    "OTCT-7968_TC_010": "Validate unauthorized upload restriction",
    "OTCT-7968_TC_011": "Validate read-only upload restriction",
    "OTCT-7968_TC_012": "Validate duplicate Trade IDs with spaces",
    "OTCT-7968_TC_013": "Validate password-field masking",
    "OTCT-7968_TC_014": "Validate password confirmation mismatch",
    "OTCT-7968_TC_015": "Validate password complexity",
    "OTCT-7968_TC_016": "Validate Password Reset button visibility",
    "OTCT-7968_TC_017": "Validate Password Reset button restriction",
    "OTCT-7968_TC_018": "Validate 50,000 Trade IDs",
    "OTCT-7968_TC_019": "Validate 49,999 Trade IDs",
    "OTCT-7968_TC_020": "Validate extremely large CSV stability",
    "OTCT-7968_TC_021": "Validate generated-password policy",
    "OTCT-7968_TC_022": "Validate password reset for same Member ID",
    "OTCT-7968_TC_023": "Validate password reset for different Member ID",
    "OTCT-7968_TC_024": "Validate REM-user password reset restriction",
    "OTCT-7968_TC_025": "Validate same-member password reset eligibility",
    "OTCT-7968_TC_026": "Validate different-member password reset restriction",
    "OTCT-7968_TC_027": "Validate REM-user password reset restriction",
    "OTCT-7968_TC_030": "Validate generated-password policy compliance",
}


INLINE_CSS = r"""
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
    --warning-text: #93370d;
    --warning-border: #fedf89;
    --page-bg: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #101828;
    --text-muted: #667085;
    --border: #d0d5dd;
    --soft-border: #eaecf0;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: "Segoe UI", Arial, sans-serif;
    background: var(--page-bg);
    color: var(--text-main);
}
.page { padding: 28px; }
.header {
    background: linear-gradient(90deg, var(--primary-dark), var(--primary));
    color: #fff;
    border-radius: 16px;
    padding: 26px 30px;
    margin-bottom: 22px;
    box-shadow: 0 4px 12px rgba(21, 94, 239, 0.18);
}
.header h1 { margin: 0; font-size: 30px; font-weight: 800; }
.header .sub { margin-top: 8px; font-size: 14px; opacity: 0.9; }
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
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
.summary-label { color: var(--text-muted); font-size: 13px; font-weight: 600; }
.summary-value { margin-top: 8px; font-size: 28px; font-weight: 800; }
.summary-pass { color: var(--success-text); }
.summary-fail { color: var(--failure-text); }
.summary-neutral { color: var(--neutral-text); }
.application-title {
    background: var(--primary-light);
    border-left: 6px solid var(--primary);
    border-radius: 12px;
    padding: 15px 18px;
    font-size: 22px;
    font-weight: 800;
    margin: 24px 0 16px;
}
.module-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
}
.module-title { font-size: 18px; font-weight: 800; margin-bottom: 14px; }
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
.test-title { font-weight: 800; font-size: 15px; }
.test-reference { margin-top: 4px; color: var(--text-muted); font-size: 13px; }
.badges { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 6px; }
.badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
}
.status-passed { background: var(--success-bg); color: var(--success-text); border: 1px solid var(--success-border); }
.status-failed { background: var(--failure-bg); color: var(--failure-text); border: 1px solid var(--failure-border); }
.status-not-run { background: var(--neutral-bg); color: var(--neutral-text); border: 1px solid var(--neutral-border); }
.count-badge { background: var(--primary-light); color: var(--primary); border: 1px solid #c7d7fe; }
.duration-badge { background: #f9fafb; color: #475467; border: 1px solid var(--neutral-border); }
details { margin-top: 10px; }
summary { cursor: pointer; color: var(--primary); font-weight: 700; margin-bottom: 10px; }
.screenshot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 14px;
}
.shot-card {
    background: #fff;
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
.shot-body { padding: 10px 12px; }
.step-name { font-weight: 800; font-size: 13px; color: #1d2939; margin-bottom: 4px; word-break: break-word; }
.file-name { color: var(--text-muted); font-size: 12px; word-break: break-all; }
.no-screenshots, .empty {
    background: var(--warning-bg);
    border: 1px solid var(--warning-border);
    color: var(--warning-text);
    border-radius: 12px;
    padding: 14px;
    font-weight: 600;
}
.footer { margin-top: 26px; color: var(--text-muted); font-size: 12px; text-align: center; }
@media (max-width: 700px) {
    .page { padding: 14px; }
    .test-header { flex-direction: column; }
    .badges { justify-content: flex-start; }
}
"""


def display_application(application):
    return {"OTC_GUI": "OTC-GUI", "MC_GUI": "MC-GUI"}.get(
        application,
        application or "Application",
    )


def load_results():
    if not os.path.isfile(RESULTS_JSON):
        return {}

    with open(RESULTS_JSON, "r", encoding="utf-8") as result_file:
        payload = json.load(result_file)

    result_map = {}
    for result in payload.get("results", []):
        application = str(result.get("application", "")).upper()
        test_id = str(result.get("id", ""))
        if application and test_id:
            result_map[(application, test_id)] = result

    return result_map


def module_label(result):
    pack = str(result.get("pack", "")).upper()
    module = str(result.get("module", "")).lower()

    if pack == "SMOKE":
        return "Smoke Test"
    if "password" in module:
        return "Password Reset Functionality"
    if "authorization" in module or "unauthorized" in module or "readonly" in module:
        return "Transaction Authorization"
    if "duplicate" in module:
        return "Duplicate Record Injection"
    if "trade_ids" in module or "large_csv" in module or "50k" in module or "49999" in module:
        return "Maximum Record Limit"
    if pack == "SECURITY":
        return "Input File Validation"
    if pack == "REGRESSION":
        return "Regression Test"
    return "Functional Test"


def readable_test_name(result):
    test_id = str(result.get("id", ""))
    if test_id in TEST_NAMES:
        return TEST_NAMES[test_id]

    module_name = str(result.get("module", "")).split(".")[-1]
    module_name = re.sub(r"^otct_\d+_", "", module_name, flags=re.IGNORECASE)
    module_name = re.sub(r"^tc\d+_", "", module_name, flags=re.IGNORECASE)
    module_name = module_name.replace("_", " ").replace("-", " ").strip()
    return module_name.title() if module_name else test_id or "Functional Test"


def infer_screenshot_key(file_name, result_map):
    lower_name = file_name.lower()

    smoke_tokens = (
        "login_logout",
        "otc_login",
        "otc_credentials",
        "otc_after_login",
        "otc_after_logout",
    )
    if any(token in lower_name for token in smoke_tokens):
        return "OTC_GUI", "OTC_SMOKE_TC001"

    mc_match = re.match(r"mc_tc(\d{1,3})_", lower_name)
    if mc_match:
        return "MC_GUI", f"OTCT-7968_TC_{int(mc_match.group(1)):03d}"

    otc_match = re.match(r"tc(\d{1,3})_", lower_name)
    if otc_match:
        return "OTC_GUI", f"OTCT-7968_TC_{int(otc_match.group(1)):03d}"

    # Last fallback: when exactly one test ran, assign unprefixed screenshots to it.
    if len(result_map) == 1:
        return next(iter(result_map.keys()))

    return None


def screenshot_step(file_name):
    stem = os.path.splitext(file_name)[0]
    stem = re.sub(r"_\d{8}_\d{6}$", "", stem)
    stem = re.sub(r"^(mc_)?tc\d{1,3}_", "", stem, flags=re.IGNORECASE)
    return stem.replace("_", " ").replace("-", " ").strip().title() or "Screenshot"


def image_data_uri(path):
    mime_type = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def collect_screenshots(result_map):
    grouped = {key: [] for key in result_map}

    if not os.path.isdir(SCREENSHOT_ROOT):
        return grouped

    for root, _, files in os.walk(SCREENSHOT_ROOT):
        for file_name in sorted(files):
            if not file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue

            key = infer_screenshot_key(file_name, result_map)
            if key is None or key not in grouped:
                continue

            absolute_path = os.path.join(root, file_name)
            grouped[key].append(
                {
                    "file_name": file_name,
                    "absolute_path": absolute_path,
                    "step_name": screenshot_step(file_name),
                    "modified_time": os.path.getmtime(absolute_path),
                }
            )

    for screenshots in grouped.values():
        screenshots.sort(key=lambda item: item["modified_time"])

    return grouped


def status_css(status):
    normalized = str(status).upper()
    if normalized == "PASSED":
        return "status-passed"
    if normalized in {"FAILED", "TIMEOUT", "ERROR"}:
        return "status-failed"
    return "status-not-run"


def build_report_html(result_map, screenshots_by_test):
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = list(result_map.items())

    total = len(results)
    passed = sum(1 for _, result in results if str(result.get("status", "")).upper() == "PASSED")
    failed = sum(
        1
        for _, result in results
        if str(result.get("status", "")).upper() in {"FAILED", "TIMEOUT", "ERROR"}
    )
    not_run = total - passed - failed
    screenshot_total = sum(len(items) for items in screenshots_by_test.values())

    grouped = {}
    for (application, test_id), result in results:
        module = module_label(result)
        grouped.setdefault(application, {}).setdefault(module, []).append(
            (test_id, result)
        )

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Playwright Execution Report</title>",
        "<style>",
        INLINE_CSS,
        "</style>",
        "</head>",
        "<body>",
        '<main class="page">',
        '<section class="header">',
        "<h1>Playwright Execution Report</h1>",
        f'<div class="sub">Generated at {html.escape(generated_at)}</div>',
        "</section>",
        '<section class="summary-grid">',
        f'<div class="summary-card"><div class="summary-label">Test Cases</div><div class="summary-value">{total}</div></div>',
        f'<div class="summary-card"><div class="summary-label">Passed</div><div class="summary-value summary-pass">{passed}</div></div>',
        f'<div class="summary-card"><div class="summary-label">Failed</div><div class="summary-value summary-fail">{failed}</div></div>',
        f'<div class="summary-card"><div class="summary-label">Not Run / Unknown</div><div class="summary-value summary-neutral">{not_run}</div></div>',
        f'<div class="summary-card"><div class="summary-label">Screenshots</div><div class="summary-value">{screenshot_total}</div></div>',
        "</section>",
    ]

    if not results:
        parts.append('<div class="empty">No test results found. Check runtime/reports/runner_results.json.</div>')

    for application, modules in grouped.items():
        parts.append(
            f'<section class="application-title">{html.escape(display_application(application))}</section>'
        )

        for module, tests in modules.items():
            module_shots = sum(
                len(screenshots_by_test.get((application, test_id), []))
                for test_id, _ in tests
            )
            parts.append('<section class="module-card">')
            parts.append(
                f'<div class="module-title">{html.escape(module)} '
                f'<span class="badge count-badge">{module_shots} screenshots</span></div>'
            )

            for test_id, result in tests:
                status = str(result.get("status", "NOT RUN")).upper()
                duration = result.get("duration_seconds")
                screenshots = screenshots_by_test.get((application, test_id), [])

                parts.append('<article class="test-card">')
                parts.append('<div class="test-header">')
                parts.append("<div>")
                parts.append(
                    f'<div class="test-title">{html.escape(readable_test_name(result))}</div>'
                )
                parts.append(
                    f'<div class="test-reference">Reference ID: {html.escape(test_id)}</div>'
                )
                parts.append("</div>")
                parts.append('<div class="badges">')
                parts.append(
                    f'<span class="badge {status_css(status)}">{html.escape(status)}</span>'
                )
                parts.append(
                    f'<span class="badge count-badge">{len(screenshots)} screenshots</span>'
                )
                if duration is not None:
                    parts.append(
                        f'<span class="badge duration-badge">{html.escape(str(duration))}s</span>'
                    )
                parts.append("</div></div>")

                parts.append("<details open><summary>View screenshots</summary>")
                if screenshots:
                    parts.append('<div class="screenshot-grid">')
                    for screenshot in screenshots:
                        safe_file = html.escape(screenshot["file_name"])
                        safe_step = html.escape(screenshot["step_name"])
                        uri = image_data_uri(screenshot["absolute_path"])
                        parts.append('<div class="shot-card">')
                        parts.append(
                            f'<img src="{uri}" alt="{safe_file}" loading="lazy">'
                        )
                        parts.append('<div class="shot-body">')
                        parts.append(f'<div class="step-name">{safe_step}</div>')
                        parts.append(f'<div class="file-name">{safe_file}</div>')
                        parts.append("</div></div>")
                    parts.append("</div>")
                else:
                    parts.append(
                        '<div class="no-screenshots">No screenshots were captured for this test case.</div>'
                    )
                parts.append("</details></article>")

            parts.append("</section>")

    parts.extend(
        [
            '<footer class="footer">Generated by Playwright Automation Runner</footer>',
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(parts)


def write_html(grouped=None, result_map=None, total_screenshots=None):
    # Compatibility wrapper for earlier runner/report versions.
    if result_map is None:
        result_map = load_results()
    screenshots_by_test = collect_screenshots(result_map)
    report_html = build_report_html(result_map, screenshots_by_test)

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as report_file:
        report_file.write(report_html)

    return REPORT_FILE


def generate_html_report():
    result_map = load_results()
    return write_html(result_map=result_map)


if __name__ == "__main__":
    report_path = generate_html_report()
    print(f"Generated HTML report: {report_path}")
