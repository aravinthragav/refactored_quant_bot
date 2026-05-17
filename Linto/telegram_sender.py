import requests

BOT_TOKEN = "8704963574:AAGOZoYjiqSPkF-FQIuuvTsUYTPgF0fPmsk"

CHANNEL_ID = "@tradingalertsAR"

BASE_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

# =========================================================
# SEND TEXT MESSAGE
# =========================================================

def send_message(text):

    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    response = requests.post(
        url,
        json=payload
    )

    print(response.text)

# =========================================================
# SEND PHOTO WITH CAPTION
# =========================================================

def send_photo(photo_path, caption=""):

    url = f"{BASE_URL}/sendPhoto"

    with open(photo_path, "rb") as photo:

        response = requests.post(
            url,
            data={
                "chat_id": CHANNEL_ID,
                "caption": caption,
                "parse_mode": "Markdown"
            },
            files={
                "photo": photo
            }
        )

    print(response.text)