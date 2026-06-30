import pandas as pd
from dhanhq import dhanhq, DhanContext
from config import CSV_URL, DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN

dhan_context = DhanContext(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
dhan = dhanhq(dhan_context)


def load_scrip_master():
    return pd.read_csv(CSV_URL, low_memory=False)


def get_fno_stocks():
    df = load_scrip_master()

    df = df[
        (df["SEM_EXM_EXCH_ID"] == "NSE") &
        (df["SEM_INSTRUMENT_NAME"].isin(["FUTSTK", "FUTIDX"]))
    ]

    df = df.drop_duplicates(subset=["SEM_TRADING_SYMBOL"])
    return df.reset_index(drop=True)


def get_live_quotes(security_ids):
    payload = {
        "NSE_FNO": security_ids
    }

    return dhan.quote_data(payload)
