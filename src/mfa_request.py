import json
import requests

from .config import settings

async def send_slack_message(title, message):
    webhook_url = settings["webhook_url"]

    slack_data = {
        "text" : title,
        "attachments": [
            {
                "fields": [
                    {
                        "value": message
                    }
                ]
            }
        ] 
    }

    headers = {'Content-Type': "application/json"}
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)