from config import DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN

print("CLIENT_ID:", repr(DHAN_CLIENT_ID))
print("CLIENT_ID LENGTH:", len(DHAN_CLIENT_ID))
print("TOKEN LENGTH:", len(DHAN_ACCESS_TOKEN))

from market_data import get_fno_stocks, get_live_quotes

print("Loading NSE F&O Stocks...")

stocks = get_fno_stocks()

print(f"Loaded {len(stocks)} F&O Stocks")

# First 5 stocks only (testing)
security_ids = stocks["SEM_SMST_SECURITY_ID"].astype(int).tolist()

print("Security IDs:", security_ids)
print(stocks[["SEM_TRADING_SYMBOL", "SEM_SMST_SECURITY_ID"]].head(5))

quotes = get_live_quotes(security_ids)

print("Quotes:")
print(quotes)

import json
print(json.dumps(quotes, indent=2))
