"""
This module provides functionality to send notifications to Slack.
"""

import json
import logging
import threading

import requests

from egse.settings import Settings

MODULE_LOGGER = logging.getLogger(__name__)

SETTINGS = Settings.load("Slack Notifications")


def _threaded_message(slack_msg: str):

    response = requests.post(
        SETTINGS.WEBHOOK, data=json.dumps(slack_msg), headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        MODULE_LOGGER.error(
            f"Request to slack returned an error {response.status_code}, "
            f"the response is: {response.text}"
        )
    else:
        MODULE_LOGGER.warning(f"Message send successfully to Slack: {slack_msg=}")


def send_message(msg: str):

    slack_msg = {"text": msg}

    thread = threading.Thread(target=_threaded_message, args=(slack_msg, ))
    thread.start()
    # no need to join the thread, it will be finished in about 500ms, but waiting for it
    # might be too long in some circumstances.
    # thread.join(timeout=1.0)


def send_alert(msg: str):
    slack_msg = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Alert*: {msg}",
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://owncloud.ster.kuleuven.be/index.php/s/bAXKHzEGNeG2FkB/preview",
                    "alt_text": "IMPORTANT"
                },
            },
        ]
    }

    thread = threading.Thread(target=_threaded_message, args=(slack_msg, ))
    thread.start()
