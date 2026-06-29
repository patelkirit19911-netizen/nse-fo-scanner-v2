import os
import requests
import pandas as pd
from dhanhq import dhanhq
import os

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)

print("✅ Dhan API Connected Successfully")

# ==========================
# CONFIG
# ==========================

DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CSV_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"

# ==========================
# TELEGRAM
# ==========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

# ==========================
# LOAD NSE F&O LIST
# ==========================

def load_fno():
    df = pd.read_csv(CSV_URL)

    df = df[
        (df["SEM_EXM_EXCH_ID"] == "NSE") &
        (df["SEM_INSTRUMENT_NAME"] == "EQUITY")
    ]

    return df

# ==========================
# START
# ==========================

print("Loading NSE Stocks...")

stocks = load_fno()

print(f"Loaded {len(stocks)} stocks")

send_telegram("✅ Scanner V2 Started Successfully")
