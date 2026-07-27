from datetime import datetime


def capture_screenshot(
    page,
    screenshot_name
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    screenshot_path = (
        f"runtime/screenshots/"
        f"{screenshot_name}_{timestamp}.png"
    )

    page.screenshot(
        path=screenshot_path
    )

    return screenshot_path