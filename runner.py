

import os
import subprocess
import sys

from common.logger import log


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
# --------------------------------------------------

OTC_GUI_SECURITY_TESTS = [
    {
        "id": "OTCT-7968_TC_001",
        "module": "otc_gui.security.otct_7968_tc001_long_filename"
    },
    {
        "id": "OTCT-7968_TC_002",
        "module": "otc_gui.security.otct_7968_tc002_trailing_space_filename"
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
        "id": "OTCT-7968_TC_026",
        "module": "otc_gui.security.otct_7968_tc026_password_reset_different_member"
    },
    {
        "id": "OTCT-7968_TC_027",
        "module": "otc_gui.security.otct_7968_tc027_rem_user_password_reset_restriction"
    },
    {
        "id": "OTCT-7968_TC_030",
        "module": "otc_gui.security.otct_7968_tc030_generated_password_policy"
    }
]


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
# Core Execution Helper
# --------------------------------------------------

def run_test_module(test):
    test_id = test["id"]
    module = test["module"]

    log("=" * 80)
    log(f"STARTING TEST [{test_id}]")
    log(f"MODULE=[{module}]")
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
    log("=" * 80)


def run_test_pack(pack_name, test_list, test_id=None):
    log(f"Executing Pack=[{pack_name}]")

    selected_tests = test_list

    if test_id:
        selected_tests = [
            test
            for test in test_list
            if test["id"] == test_id
        ]

        if not selected_tests:
            raise Exception(
                f"TEST_ID=[{test_id}] was not found in pack [{pack_name}]"
            )

    log(f"Total tests selected=[{len(selected_tests)}]")

    for index, test in enumerate(selected_tests, start=1):
        log(
            f"Executing test [{index}/{len(selected_tests)}] "
            f"ID=[{test['id']}]"
        )

        run_test_module(test)


# --------------------------------------------------
# Application Pack Functions
# --------------------------------------------------

def run_otc_smoke(test_id=None):
    run_test_pack(
        "OTC_GUI_SMOKE",
        OTC_GUI_SMOKE_TESTS,
        test_id=test_id
    )


def run_otc_security(test_id=None):
    run_test_pack(
        "OTC_GUI_SECURITY",
        OTC_GUI_SECURITY_TESTS,
        test_id=test_id
    )


def run_otc_all(test_id=None):
    log("Executing OTC GUI ALL Pack...")

    run_otc_smoke(test_id=test_id)
    run_otc_security(test_id=test_id)


def run_mc_security(test_id=None):
    run_test_pack(
        "MC_GUI_SECURITY",
        MC_GUI_SECURITY_TESTS,
        test_id=test_id
    )


def run_mc_all(test_id=None):
    log("Executing MC GUI ALL Pack...")

    # Currently MC_GUI has only SECURITY configured.
    # Add MC_GUI_SMOKE here later if needed.
    run_mc_security(test_id=test_id)


def run_all_security(test_id=None):
    log("Executing ALL SECURITY Packs...")

    if test_id:
        matching_tests = []

        matching_tests.extend(
            [
                test
                for test in OTC_GUI_SECURITY_TESTS
                if test["id"] == test_id
            ]
        )

        matching_tests.extend(
            [
                test
                for test in MC_GUI_SECURITY_TESTS
                if test["id"] == test_id
            ]
        )

        if not matching_tests:
            raise Exception(
                f"TEST_ID=[{test_id}] was not found in any SECURITY pack"
            )

        run_test_pack(
            "ALL_SECURITY_FILTERED",
            matching_tests
        )

        return

    run_otc_security()
    run_mc_security()


def run_all_all(test_id=None):
    log("Executing APPLICATION=ALL PACK=ALL...")

    if test_id:
        matching_tests = []

        all_registered_tests = (
            OTC_GUI_SMOKE_TESTS +
            OTC_GUI_SECURITY_TESTS +
            MC_GUI_SECURITY_TESTS
        )

        matching_tests.extend(
            [
                test
                for test in all_registered_tests
                if test["id"] == test_id
            ]
        )

        if not matching_tests:
            raise Exception(
                f"TEST_ID=[{test_id}] was not found in any registered pack"
            )

        run_test_pack(
            "ALL_ALL_FILTERED",
            matching_tests
        )

        return

    run_otc_smoke()
    run_otc_security()
    run_mc_security()


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    application = os.getenv(
        "APPLICATION",
        "OTC_GUI"
    ).upper()

    pack = os.getenv(
        "PACK",
        "SMOKE"
    ).upper()

    test_id = os.getenv(
        "TEST_ID",
        ""
    ).strip()

    log(f"APPLICATION=[{application}] PACK=[{pack}] TEST_ID=[{test_id}]")

    try:
        if application == "OTC_GUI" and pack == "SMOKE":
            run_otc_smoke(
                test_id=test_id or None
            )

        elif application == "OTC_GUI" and pack == "SECURITY":
            run_otc_security(
                test_id=test_id or None
            )

        elif application == "OTC_GUI" and pack == "ALL":
            run_otc_all(
                test_id=test_id or None
            )

        elif application == "MC_GUI" and pack == "SECURITY":
            run_mc_security(
                test_id=test_id or None
            )

        elif application == "MC_GUI" and pack == "ALL":
            run_mc_all(
                test_id=test_id or None
            )

        elif application == "ALL" and pack == "SECURITY":
            run_all_security(
                test_id=test_id or None
            )

        elif application == "ALL" and pack == "ALL":
            run_all_all(
                test_id=test_id or None
            )

        else:
            raise Exception(
                f"No runner configured for APPLICATION=[{application}] "
                f"PACK=[{pack}]"
            )

        log("Runner completed successfully")

    except Exception as error:
        log(f"Runner failed: {error}")
        sys.exit(1)