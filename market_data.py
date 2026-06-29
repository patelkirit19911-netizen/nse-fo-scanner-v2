import pandas as pd
import requests
from config import CSV_URL

def load_scrip_master():
    """Load Dhan Scrip Master"""
    return pd.read_csv(CSV_URL, low_memory=False)

def get_fno_stocks():
    df = load_scrip_master()

    df = df[
        (df["SEM_EXM_EXCH_ID"] == "NSE") &
        (df["SEM_INSTRUMENT_NAME"].isin(["FUTSTK", "FUTIDX"]))
    ]

    df = df.drop_duplicates(subset=["SEM_TRADING_SYMBOL"])

    return df.reset_index(drop=True)
