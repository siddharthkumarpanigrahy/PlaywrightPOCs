import os
import subprocess

from common.logger import log


def run_otc_smoke():

    log("Executing OTC GUI Smoke Pack...")

    subprocess.run(
        [
            "python3",
            "-m",
            "otc_gui.smoke.tc001_login_logout"
        ],
        check=True
    )

def run_otc_security():
    log("Executing OTC GUI Security Pack...")

    subprocess.run(
        [
            "python3",
            "-m",
            "otc_gui.security.otct_7968_tc001_long_filename"
        ],
        check=True
    )    


if __name__ == "__main__":

    application = os.getenv(
        "APPLICATION",
        "OTC_GUI"
    )

    pack = os.getenv(
        "PACK",
        "SMOKE"
    )
    log(f"APPLICATION=[{application}] PACK=[{pack}]")


    if (
        application == "OTC_GUI"
        and pack == "SMOKE"
    ):

        run_otc_smoke()

    elif (
        application == "OTC_GUI"
        and pack == "SECURITY"
    ):
        run_otc_security()

    else:

        log(
            f"No runner configured for "
            f"{application} / {pack}"
        )