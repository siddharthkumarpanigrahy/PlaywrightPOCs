from datetime import datetime


def generate_report(
    test_name,
    result
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_name = (
        f"runtime/reports/"
        f"report_{timestamp}.txt"
    )

    with open(
        report_name,
        "w"
    ) as report:

        report.write(
            f"Test Case : {test_name}\n"
        )

        report.write(
            f"Result    : {result}\n"
        )

        report.write(
            f"Executed  : {timestamp}\n"
        )

    return report_name