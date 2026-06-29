import requests
from config import BOT_TOKEN, CHAT_ID

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        },
        timeout=15
    )

    return response.status_code == 200
