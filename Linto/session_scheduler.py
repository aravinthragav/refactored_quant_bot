import datetime as dt

from news_engine import (
    fetch_news,
    summarize_news
)

from telegram_sender import (
    send_message
)

LAST_SESSION_ALERT = {}

SESSIONS = {

    "Asia": 0,

    "London": 7,

    "NewYork": 13
}

def send_session_briefings():

    now = dt.datetime.now(
        dt.timezone.utc
    )

    current_hour = now.hour

    for session_name, hour in SESSIONS.items():

        if current_hour != hour:
            continue

        session_key = (
            f"{session_name}_{now.date()}"
        )

        if session_key in LAST_SESSION_ALERT:

            continue

        LAST_SESSION_ALERT[
            session_key
        ] = True

        for asset in [
            "BTC",
            "GOLD"
        ]:

            articles = fetch_news(asset)

            summary = summarize_news(
                articles
            )

            text = f"""
📰 {asset} Session Briefing

🌍 Session:
{session_name}

"""

            for line in summary:

                text += f"{line}\n"

            send_message(text)