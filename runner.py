import os
import subprocess
import sys
from datetime import datetime

from common.logger import log
from common.html_report import generate_html_report


# --------------------------------------------------
# Test Registry - OTC GUI Smoke
# --------------------------------------------------

OTC_GUI_SMOKE_TESTS = [
    {
        "id": "OTC_SMOKE_TC001",
        "module": "otc_gui.smoke.tc001_login_logout"
    }
]


# --------------------------------------------------
# Test Registry - OTC GUI Security
# Based on current otc_gui/security folder.
# --------------------------------------------------

OTC_GUI_SECURITY_TESTS = [
    {
        "id": "OTCT-7968_TC_001",
        "module": "otc_gui.security.otct_7968_tc001_long_filename"
    },
    {
        "id": "OTCT-7968_TC_002",
        "module": "otc_gui.security.otct_7968_tc002_filename_spaces"
    },
    {
        "id": "OTCT-7968_TC_003",
        "module": "otc_gui.security.otct_7968_tc003_empty_file"
    },
    {
        "id": "OTCT-7968_TC_004",
        "module": "otc_gui.security.otct_7968_tc004_missing_header"
    },
    {
        "id": "OTCT-7968_TC_005",
        "module": "otc_gui.security.otct_7968_tc005_extra_columns"
    },
    {
        "id": "OTCT-7968_TC_006",
        "module": "otc_gui.security.otct_7968_tc006_special_chars"
    },
    {
        "id": "OTCT-7968_TC_007",
        "module": "otc_gui.security.otct_7968_tc007_unicode_emoji"
    },
    {
        "id": "OTCT-7968_TC_008",
        "module": "otc_gui.security.otct_7968_tc008_formula_injection"
    },
    {
        "id": "OTCT-7968_TC_009",
        "module": "otc_gui.security.otct_7968_tc009_hyperlinks_objects"
    },
    {
        "id": "OTCT-7968_TC_010",
        "module": "otc_gui.security.otct_7968_tc010_unauthorized_upload"
    },
    {
        "id": "OTCT-7968_TC_011",
        "module": "otc_gui.security.otct_7968_tc011_readonly_upload_restriction"
    },
    {
        "id": "OTCT-7968_TC_012",
        "module": "otc_gui.security.otct_7968_tc012_duplicate_trade_ids_spaces"
    },
    {
        "id": "OTCT-7968_TC_013",
        "module": "otc_gui.security.otct_7968_tc013_password_field_masking"
    },
    {
        "id": "OTCT-7968_TC_014",
        "module": "otc_gui.security.otct_7968_tc014_password_confirm_mismatch"
    },
    {
        "id": "OTCT-7968_TC_015",
        "module": "otc_gui.security.otct_7968_tc015_password_complexity"
    },
    {
        "id": "OTCT-7968_TC_016",
        "module": "otc_gui.security.otct_7968_tc016_password_reset_button_visible"
    },
    {
        "id": "OTCT-7968_TC_017",
        "module": "otc_gui.security.otct_7968_tc017_password_reset_button_hidden"
    },
    {
        "id": "OTCT-7968_TC_018",
        "module": "otc_gui.security.otct_7968_tc018_50k_trade_ids"
    },
    {
        "id": "OTCT-7968_TC_019",
        "module": "otc_gui.security.otct_7968_tc019_49999_trade_ids"
    },
    {
        "id": "OTCT-7968_TC_020",
        "module": "otc_gui.security.otct_7968_tc020_extremely_large_csv_stability"
    },
    {
        "id": "OTCT-7968_TC_021",
        "module": "otc_gui.security.otct_7968_tc021_generated_password_policy"
    },
    {
        "id": "OTCT-7968_TC_022",
        "module": "otc_gui.security.otct_7968_tc022_password_reset_same_member"
    },
    {
        "id": "OTCT-7968_TC_023",
        "module": "otc_gui.security.otct_7968_tc023_password_reset_different_member"
    },
    {
        "id": "OTCT-7968_TC_024",
        "module": "otc_gui.security.otct_7968_tc024_password_reset_rem_user"
    }
]


# --------------------------------------------------
# Test Registry - OTC GUI Regression
# Add tests here when implemented.
# --------------------------------------------------

OTC_GUI_REGRESSION_TESTS = []


# --------------------------------------------------
# Test Registry - MC GUI Smoke
# Add tests here when implemented.
# --------------------------------------------------

MC_GUI_SMOKE_TESTS = []


# --------------------------------------------------
# Test Registry - MC GUI Security
# --------------------------------------------------

MC_GUI_SECURITY_TESTS = [
    {
        "id": "OTCT-7968_TC_001",
        "module": "mc_gui.security.otct_7968_tc001_long_filename"
    },
    {
        "id": "OTCT-7968_TC_002",
        "module": "mc_gui.security.otct_7968_tc002_filename_spaces"
    },
    {
        "id": "OTCT-7968_TC_003",
        "module": "mc_gui.security.otct_7968_tc003_empty_file"
    },
    {
        "id": "OTCT-7968_TC_004",
        "module": "mc_gui.security.otct_7968_tc004_missing_header"
    },
    {
        "id": "OTCT-7968_TC_005",
        "module": "mc_gui.security.otct_7968_tc005_extra_columns"
    },
    {
        "id": "OTCT-7968_TC_006",
        "module": "mc_gui.security.otct_7968_tc006_special_characters"
    },
    {
        "id": "OTCT-7968_TC_007",
        "module": "mc_gui.security.otct_7968_tc007_unicode_emoji"
    },
    {
        "id": "OTCT-7968_TC_008",
        "module": "mc_gui.security.otct_7968_tc008_formula_injection"
    },
    {
        "id": "OTCT-7968_TC_009",
        "module": "mc_gui.security.otct_7968_tc009_hyperlinks_objects"
    }
]


# --------------------------------------------------
# Test Registry - MC GUI Regression
# Add tests here when implemented.
# --------------------------------------------------

MC_GUI_REGRESSION_TESTS = []


# --------------------------------------------------
# Registry Map
# --------------------------------------------------

TEST_REGISTRY = {
    "OTC_GUI": {
        "SMOKE": OTC_GUI_SMOKE_TESTS,
        "SECURITY": OTC_GUI_SECURITY_TESTS,
        "REGRESSION": OTC_GUI_REGRESSION_TESTS
    },
    "MC_GUI": {
        "SMOKE": MC_GUI_SMOKE_TESTS,
        "SECURITY": MC_GUI_SECURITY_TESTS,
        "REGRESSION": MC_GUI_REGRESSION_TESTS
    }
}


VALID_APPLICATIONS = [
    "OTC_GUI",
    "MC_GUI"
]

VALID_PACKS = [
    "SMOKE",
    "SECURITY",
    "REGRESSION"
]


# --------------------------------------------------
# Utility Helpers
# --------------------------------------------------

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_csv_env(value, default_value):
    if not value:
        value = default_value

    value = value.strip()

    if not value:
        return []

    return [
        item.strip().upper()
        for item in value.split(",")
        if item.strip()
    ]


def parse_test_ids(value):
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def remove_duplicates_preserve_order(values):
    seen = set()
    result = []

    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)

    return result


def expand_applications(application_values):
    expanded = []

    for application in application_values:
        if application == "ALL":
            expanded.extend(VALID_APPLICATIONS)
        elif application in VALID_APPLICATIONS:
            expanded.append(application)
        else:
            raise Exception(
                f"Unsupported APPLICATION value: [{application}]"
            )

    return remove_duplicates_preserve_order(expanded)


def expand_packs(pack_values):
    expanded = []

    for pack in pack_values:
        if pack == "ALL":
            expanded.extend(VALID_PACKS)
        elif pack in VALID_PACKS:
            expanded.append(pack)
        else:
            raise Exception(
                f"Unsupported PACK value: [{pack}]"
            )

    return remove_duplicates_preserve_order(expanded)


def build_execution_plan(applications, packs, test_ids):
    execution_plan = []

    for application in applications:
        for pack in packs:
            test_list = TEST_REGISTRY.get(
                application,
                {}
            ).get(
                pack,
                []
            )

            pack_name = f"{application}_{pack}"

            if not test_list:
                log(
                    f"Pack [{pack_name}] is not implemented or has no tests. "
                    "Skipping."
                )
                continue

            selected_tests = test_list

            if test_ids:
                selected_tests = [
                    test
                    for test in test_list
                    if test["id"] in test_ids
                ]

                if not selected_tests:
                    log(
                        f"No matching TEST_ID found in pack [{pack_name}]. "
                        f"Requested TEST_ID values={test_ids}. Skipping."
                    )
                    continue

            for test in selected_tests:
                execution_plan.append(
                    {
                        "application": application,
                        "pack": pack,
                        "pack_name": pack_name,
                        "id": test["id"],
                        "module": test["module"]
                    }
                )

    return execution_plan


# --------------------------------------------------
# Core Execution Helper
# --------------------------------------------------

def run_test_module(test):
    test_id = test["id"]
    module = test["module"]
    application = test["application"]
    pack = test["pack"]

    log("=" * 80)
    log(f"STARTING TEST [{test_id}]")
    log(f"APPLICATION=[{application}] PACK=[{pack}]")
    log(f"MODULE=[{module}]")
    log(f"START_TIME=[{current_time()}]")
    log("=" * 80)

    subprocess.run(
        [
            "python3",
            "-m",
            module
        ],
        check=True
    )

    log("=" * 80)
    log(f"COMPLETED TEST [{test_id}]")
    log(f"END_TIME=[{current_time()}]")
    log("=" * 80)


def execute_plan(execution_plan, stop_on_fail):
    results = []
    total = len(execution_plan)

    log(f"Total tests selected=[{total}]")

    for index, test in enumerate(execution_plan, start=1):
        test_id = test["id"]
        module = test["module"]
        application = test["application"]
        pack = test["pack"]

        log(
            f"Executing test [{index}/{total}] "
            f"APPLICATION=[{application}] PACK=[{pack}] "
            f"ID=[{test_id}]"
        )

        try:
            run_test_module(test)

            results.append(
                {
                    "application": application,
                    "pack": pack,
                    "id": test_id,
                    "module": module,
                    "status": "PASSED"
                }
            )

        except subprocess.CalledProcessError as error:
            log(
                f"TEST FAILED: APPLICATION=[{application}] "
                f"PACK=[{pack}] ID=[{test_id}] "
                f"MODULE=[{module}] EXIT_CODE=[{error.returncode}]"
            )

            results.append(
                {
                    "application": application,
                    "pack": pack,
                    "id": test_id,
                    "module": module,
                    "status": "FAILED",
                    "exit_code": error.returncode
                }
            )

            if stop_on_fail:
                log("STOP_ON_FAIL is enabled. Stopping execution.")
                break

    return results


def write_summary(results):
    os.makedirs(
        "runtime/reports",
        exist_ok=True
    )

    summary_file = "runtime/reports/runner_summary.txt"

    total = len(results)

    passed = len(
        [
            result
            for result in results
            if result["status"] == "PASSED"
        ]
    )

    failed = total - passed

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as report:
        report.write("Runner Summary\n")
        report.write("=" * 80 + "\n")
        report.write(f"Generated At : {current_time()}\n")
        report.write(f"Total        : {total}\n")
        report.write(f"Passed       : {passed}\n")
        report.write(f"Failed       : {failed}\n")
        report.write("\n")

        for result in results:
            report.write(
                f"{result['application']} | "
                f"{result['pack']} | "
                f"{result['id']} | "
                f"{result['status']} | "
                f"{result['module']}\n"
            )

    log("=" * 80)
    log("RUNNER SUMMARY")
    log("=" * 80)
    log(f"Total=[{total}] Passed=[{passed}] Failed=[{failed}]")
    log(f"Summary file=[{summary_file}]")
    log("=" * 80)

    return failed


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    raw_application = os.getenv(
        "APPLICATION",
        "OTC_GUI"
    )

    raw_pack = os.getenv(
        "PACK",
        "SMOKE"
    )

    raw_test_id = os.getenv(
        "TEST_ID",
        ""
    )

    stop_on_fail_raw = os.getenv(
        "STOP_ON_FAIL",
        "false"
    ).lower()

    stop_on_fail = stop_on_fail_raw in [
        "true",
        "1",
        "yes",
        "y"
    ]

    log(
        f"APPLICATION=[{raw_application}] "
        f"PACK=[{raw_pack}] "
        f"TEST_ID=[{raw_test_id}] "
        f"STOP_ON_FAIL=[{stop_on_fail}]"
    )

    try:
        application_values = parse_csv_env(
            raw_application,
            "OTC_GUI"
        )

        pack_values = parse_csv_env(
            raw_pack,
            "SMOKE"
        )

        test_ids = parse_test_ids(
            raw_test_id
        )

        applications = expand_applications(
            application_values
        )

        packs = expand_packs(
            pack_values
        )

        log(f"Resolved applications={applications}")
        log(f"Resolved packs={packs}")
        log(f"Resolved test_ids={test_ids}")

        execution_plan = build_execution_plan(
            applications,
            packs,
            test_ids
        )

        if not execution_plan:
            raise Exception(
                "No tests selected for execution. "
                "Check APPLICATION, PACK, and TEST_ID parameters."
            )

        results = execute_plan(
            execution_plan,
            stop_on_fail
        )

        failed_count = write_summary(
            results
        )

        screenshot_report = generate_html_report()

        log(
            f"Screenshot HTML report generated=[{screenshot_report}]"
        )

        if failed_count > 0:
            log(
                f"Runner completed with failures. "
                f"Failed count=[{failed_count}]"
            )
            sys.exit(1)

        log("Runner completed successfully")
        sys.exit(0)

    except Exception as error:
        log(f"Runner failed: {error}")

        try:
            screenshot_report = generate_html_report()
            log(
                f"Screenshot HTML report generated after failure="
                f"[{screenshot_report}]"
            )
        except Exception as report_error:
            log(
                f"Failed to generate screenshot HTML report: {report_error}"
            )

        sys.exit(1)
