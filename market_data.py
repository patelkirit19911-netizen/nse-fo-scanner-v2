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
    return pd.read_csv(CSV_URL, low_memory=False)


def get_fno_stocks():
    df = load_scrip_master()

    df = df[
    (df["SEM_EXM_EXCH_ID"] == "NSE") &
    (df["SEM_INSTRUMENT_NAME"].isin(["FUTSTK", "FUTIDX"])) &
    (~df["SEM_TRADING_SYMBOL"].str.contains("NSETEST", na=False))
    ]

    df = df.drop_duplicates(subset=["SEM_TRADING_SYMBOL"])

    return df.reset_index(drop=True)


def get_live_quotes(security_ids):
    print("Security IDs:", len(security_ids))
    print("First Security ID:", security_ids[0])

    payload = {
    "NSE_FNO": security_ids
}

    print("Payload:", payload)

    response = dhan.quote_data(payload)
    print("Response:", response)

    return response

def get_historical_data(security_id, from_date, to_date):
    print("Calling historical API...")
    print("Security ID:", security_id)
    print("From:", from_date)
    print("To:", to_date)

    try:
        response = dhan.historical_daily_data(
            security_id=security_id,
            exchange_segment=dhan.NSE_FNO,
            from_date=from_date,
            to_date=to_date
        )
        print("History Response:", response)
        return response
    except Exception as e:
        print("Historical Exception:", e)
        raise
