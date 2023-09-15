from egse import slack
from egse.system import Timer


def test_slack_send_message():

    with Timer("Slack message"):
        slack.send_message("Test message from CGSE unit test.")


def test_slack_send_alert():

    with Timer("Slack message"):
        slack.send_alert(
            "The task stopped on the TCS EGSE.\n\n"
            "Check the MMI on the TCS EGSE, if there are no errors\n"
            "re-start the task with the command: `tcs.start_task()`")
