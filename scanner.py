import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("Scanner V2 Started")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "✅ NSE FO Scanner V2 Test Successful"
    },
    timeout=20
)

print("Telegram Status:", response.status_code)
print(response.text)
