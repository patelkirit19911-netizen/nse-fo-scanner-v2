import pandas as pd
from dhanhq import dhanhq, DhanContext
from config import CSV_URL, DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN

dhan_context = DhanContext(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
dhan = dhanhq(dhan_context)
print("CLIENT_ID:", DHAN_CLIENT_ID)
print("TOKEN LENGTH:", len(DHAN_ACCESS_TOKEN) if DHAN_ACCESS_TOKEN else 0)
print("TOKEN START:", DHAN_ACCESS_TOKEN[:10] if DHAN_ACCESS_TOKEN else "None")
print("TOKEN END:", DHAN_ACCESS_TOKEN[-10:] if DHAN_ACCESS_TOKEN else "None")

def load_scrip_master():
    import requests
    from io import StringIO

    url = "https://drive.google.com/uc?export=download&id=1DTjGJji58MFRibjWIN_3b4wzU6ZbUmBz"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return pd.read_csv(StringIO(response.text), low_memory=False)
def get_nifty_stocks():
    df = load_scrip_master()

    df = df[
    (df["SEM_EXM_EXCH_ID"] == "NSE") &
    (df["SEM_SEGMENT"] == "E") &(~df["SEM_TRADING_SYMBOL"].str.contains("NSETEST", na=False))]

    print(df["SEM_SEGMENT"].value_counts())
    print(df.head())
    print(df[["SEM_TRADING_SYMBOL", "SEM_SMST_SECURITY_ID"]].head(20))
    return df.reset_index(drop=True)
    
def get_live_quotes(security_ids):
    print("Security IDs:", len(security_ids))
    print("First Security ID:", security_ids[0])

    payload = {"NSE_EQ": security_ids}
    
    print(type(payload))
    print(payload)
    print(type(security_ids[0]))
    print("Payload:", payload)
    
    response = dhan.quote_data(payload)
    if response.get("status") != "success":
        raise Exception(f"Quote API Error: {response}")
    return response["data"]

def get_historical_data(security_id, from_date, to_date):
    print("Calling historical API...")
    print("Security ID:", security_id)
    print("From:", from_date)
    print("To:", to_date)

    try:
        response = dhan.historical_daily_data(
            security_id=security_id,
            exchange_segment="NSE_EQ",
            instrument_type="EQUITY",
            from_date=from_date,
            to_date=to_date
        )
        print("History Response:", response)
        print("History Keys:", response.keys() if isinstance(response, dict) else type(response))
        return response
    except Exception as e:
        print("Historical Exception:", e)
        raise
