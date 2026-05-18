# monitoring.py

import requests
import traceback
import socket
import datetime as dt

BOT_TOKEN = "8704963574:AAGOZoYjiqSPkF-FQIuuvTsUYTPgF0fPmsk"

CHAT_ID = "8704963574"

def send_alert(
    title,
    message
):

    full_message = f"""
🚨 {title}

{message}

🖥 Host:
{socket.gethostname()}

🕒 UTC:
{dt.datetime.now(dt.timezone.utc)}
"""

    try:

        requests.post(

            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",

            json={

                "chat_id": CHAT_ID,

                "text": full_message
            },

            timeout=10
        )

    except Exception as e:

        print(
            "Alert failed:",
            e
        )

def send_exception_alert(
    e
):

    send_alert(

        "BOT FAILURE",

        traceback.format_exc()
    )