from market_data import get_fno_stocks, get_live_quotes
import pandas as pd

print("Loading NSE F&O Stocks...")

stocks = get_fno_stocks()
print(f"Loaded {len(stocks)} F&O Stocks")

# All Security IDs
security_ids = stocks["SEM_SMST_SECURITY_ID"].astype(int).tolist()

print("Getting Live Quotes...")

quotes = get_live_quotes(security_ids)
rows = []

for security_id, data in quotes["data"]["data"]["NSE_FNO"].items():
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
# Merge live data with stock master

merged_df = stocks.merge(
    live_df,
    left_on="SEM_SMST_SECURITY_ID",
    right_on="security_id",
    how="inner"
)

print(merged_df[[
    "SEM_TRADING_SYMBOL",
    "last_price",
    "volume",
    "oi"
]].head())
# Top OI Stocks

top_oi = merged_df.sort_values("oi", ascending=False).head(10)

print("\nTop 10 OI Stocks")
print(top_oi[[
    "SEM_TRADING_SYMBOL",
    "last_price",
    "volume",
    "oi"
]])
# Price Change %

merged_df["price_change_pct"] = (
    (merged_df["last_price"] - merged_df["SEM_CLOSE_PRICE"]) /
    merged_df["SEM_CLOSE_PRICE"]
) * 100

print("\nTop 10 Price Gainers")

print(
    merged_df.sort_values("price_change_pct", ascending=False)[[
        "SEM_TRADING_SYMBOL",
        "last_price",
        "SEM_CLOSE_PRICE",
        "price_change_pct"
    ]].head(10)
)
