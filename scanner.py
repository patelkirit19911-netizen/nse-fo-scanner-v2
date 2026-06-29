from market_data import get_fno_stocks, get_live_quotes

print("Loading NSE F&O Stocks...")

stocks = get_fno_stocks()

print(f"Loaded {len(stocks)} F&O Stocks")

# First 5 stocks only (testing)
security_ids = stocks["SEM_SMST_SECURITY_ID"].head(5).tolist()

quotes = get_live_quotes(security_ids)

print(quotes)
import json

print(json.dumps(quotes, indent=2))
