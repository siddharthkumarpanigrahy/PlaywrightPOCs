import os

from common.login import login
from common.logout import logout
from common.browser import launch_browser
from common.logger import log
from locators.otc_gui.portfolio_transfer_locators import (
    PortfolioTransferLocators,
)

# Remove proxy settings inherited from the environment
for proxy in (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy"
):
    os.environ.pop(proxy, None)

os.environ["NO_PROXY"] = "10.130.209.10"
os.environ["no_proxy"] = "10.130.209.10"

playwright, browser, context, page = launch_browser()

page.on(
    "requestfailed",
    lambda request: log(
        f"FAILED: {request.url} - {request.failure}"
    )
)

try:

    log("Starting OTCT-7968_TC_001")

    # Login
    login(page)

    page.wait_for_timeout(3000)

    # Portfolio Transfer menu
    page.click("a[href='#portfolio']")

    page.wait_for_timeout(2000)

    # Portfolio Transfer Entry
    page.locator(
    ".BlueTabPanelAppearance-BlueTabPanelStyle-tabStripText"
).filter(
    has_text="Portfolio Transfer Entry"
).first.click()

    page.wait_for_timeout(2000)

    # Entry Type dropdown
    page.locator(
        PortfolioTransferLocators.ENTRY_TYPE
    ).click()

    page.wait_for_timeout(1000)

    # Portfolio Upload
    page.get_by_text(
        "Portfolio Upload"
    ).click()

    page.wait_for_timeout(2000)

    # long file path
    long_filename_file = (
        "./test_data/otc_gui/security/portfolio transfer/PortfolioUpload_20260727asdfqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmadsasssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss.csv"
    )

    # determine the length of the long filename
    print("Filename Length = ",
          len(os.path.basename(long_filename_file))
          )
    

    # Uplload file with long filename
    page.locator(
        PortfolioTransferLocators.FILE_UPLOAD
    ).set_input_files(long_filename_file)

    page.wait_for_timeout(5000)

    page.screenshot(
        path="runtime/screenshots/"
             "otct_7968_tc001_after_upload.png"
    )

    log("File uploaded successfully")

    logout(page)

except Exception as e:

    log(f"TEST FAILED: {e}")

finally:

    browser.close()
    playwright.stop()


    '''
    Test Case: OTCT-7968_TC_001

Objective:
Validate upload of file with filename length >255 characters.

Actual Result:
File cannot be created/accessed by the operating system.
Automation fails with:
[Errno 36] File name too long

Application Behaviour:
Not testable because OTC_GUI never receives the file.

Conclusion:
This scenario is blocked at OS/File System level and should be discussed with BA/Product Owner/Test Lead to determine whether the test case is still valid.
    
    '''