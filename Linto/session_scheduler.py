import datetime as dt

from news_engine import (
    fetch_news,
    summarize_news
)

from telegram_sender import (
    send_message
)

from asset_configs import ASSETS

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

        # Generate the daily blog report at London (07:00 UTC) and NewYork (13:00 UTC) session starts
        if session_name in ["London", "NewYork"]:
            try:
                from blog_generator import generate_blog_report
                print(f"Triggering automatic daily blog generation for {session_name} session...")
                generate_blog_report()
            except Exception as e:
                print(f"Failed to generate blog report for {session_name} session: {e}")

        for asset in ASSETS.keys():
            # Skip GOLD session briefings on weekends (Saturday=5, Sunday=6)
            if asset == "GOLD" and dt.datetime.now().weekday() in [5, 6]:
                continue

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