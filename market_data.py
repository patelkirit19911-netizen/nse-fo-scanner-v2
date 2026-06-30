import pandas as pd
import requests

from config import CSV_URL
from dhanhq import dhanhq, DhanContext
from config import DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN

dhan_context = DhanContext(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
dhan = dhanhq(dhan_context)


def load_scrip_master():
    """Load Dhan Scrip Master"""
    return pd.read_csv(CSV_URL, low_memory=False)
def test_dhan():
    return "✅ Dhan API Connected"
def get_fno_stocks():
    df = load_scrip_master()

    df = df[
        (df["SEM_EXM_EXCH_ID"] == "NSE") &
        (df["SEM_INSTRUMENT_NAME"].isin(["FUTSTK", "FUTIDX"]))
    ]

    df = df.drop_duplicates(subset=["SEM_TRADING_SYMBOL"])

    return df.reset_index(drop=True)
def get_live_quotes(security_ids):
    url = "https://api.dhan.co/v2/marketfeed/ohlc"

    headers = {
    "access-token": DHAN_ACCESS_TOKEN.strip(),
    "client-id": str(DHAN_CLIENT_ID).strip(),
    "Content-Type": "application/json"
    }

    print(repr(headers))

    payload = {
        "NSE_FNO": security_ids
    }
    print("CLIENT_ID =", repr(DHAN_CLIENT_ID))
    print("TOKEN =", repr(DHAN_ACCESS_TOKEN))
    print("CLIENT_ID TYPE =", type(DHAN_CLIENT_ID))
    print("TOKEN TYPE =", type(DHAN_ACCESS_TOKEN))
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
