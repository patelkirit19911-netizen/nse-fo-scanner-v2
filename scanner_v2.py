from market_data import get_fno_stocks, get_live_quotes
import pandas as pd

print("Loading NSE F&O Stocks...")

stocks = get_fno_stocks()
print(f"Loaded {len(stocks)} F&O Stocks")

# All Security IDs
security_ids = stocks["SEM_SMST_SECURITY_ID"].astype(int).tolist()

print("Getting Live Quotes...")

quotes = get_live_quotes(security_ids)

import json
print(json.dumps(quotes, indent=2))
exit()

for security_id, data in quotes["data"]["NSE_FNO"].items():

    rows.append({
        "security_id": int(security_id),
        "last_price": data.get("last_price", 0),
        "volume": data.get("volume", 0),
        "oi": data.get("oi", 0),
        "buy_qty": data.get("buy_quantity", 0),
        "sell_qty": data.get("sell_quantity", 0)
    })

live_df = pd.DataFrame(rows)

print(live_df.head())
print(f"Live Quotes Loaded: {len(live_df)}")
