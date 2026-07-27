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


if __name__ == "__main__":

    application = os.getenv(
        "APPLICATION",
        "OTC_GUI"
    )

    pack = os.getenv(
        "PACK",
        "SMOKE"
    )

    if (
        application == "OTC_GUI"
        and pack == "SMOKE"
    ):

        run_otc_smoke()

    else:

        log(
            f"No runner configured for "
            f"{application} / {pack}"
        )