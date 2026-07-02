from market_data import get_nifty_stocks, get_live_quotes, get_historical_data
import ta
import pandas as pd
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
from telegram import send_message
from datetime import datetime, timedelta, timezone

print("Loading NSE F&O Stocks...")

stocks = get_nifty_stocks()
print(f"Loaded {len(stocks)} NIFTY Stocks")

# All Security IDs
security_ids = stocks["SEM_SMST_SECURITY_ID"].astype(int).tolist()

print("Getting Live Quotes...")

quotes = get_live_quotes(security_ids)
# print(quotes)
rows = []

for security_id, data in quotes["data"]["data"]["NSE_EQ"].items():
    rows.append({
        "security_id": int(security_id),
        "last_price": data.get("last_price", 0),
        "volume": data.get("volume", 0),
        "buy_qty": data.get("buy_quantity", 0),
        "sell_qty": data.get("sell_quantity", 0)
    })

live_df = pd.DataFrame(rows)

print(live_df.head())
# print(f"Live Quotes Loaded: {len(live_df)}")
# Merge live data with stock master
print(stocks["SEM_SMST_SECURITY_ID"].head(10))
# print(live_df["security_id"].head(10))
merged_df = stocks.merge(
    live_df,
    left_on="SEM_SMST_SECURITY_ID",
    right_on="security_id",
    how="inner"
)
# VWAP Filter
merged_df["high"] = merged_df["last_price"]
merged_df["low"] = merged_df["last_price"]
merged_df["close"] = merged_df["last_price"]

merged_df["vwap"] = ta.volume.VolumeWeightedAveragePrice(
    high=merged_df["high"],
    low=merged_df["low"],
    close=merged_df["close"],
    volume=merged_df["volume"]
).volume_weighted_average_price()

# VWAP Filter (Temporary Disabled)

# merged_df = merged_df[
#     merged_df["last_price"] > merged_df["vwap"]
# ]

# EMA 20 / EMA 50 Filter (Temporary Disabled)
 


#merged_df = merged_df[
#     (merged_df["last_price"] > merged_df["ema20"]) &
 #    (merged_df["ema20"] > merged_df["ema50"])
#]
print(merged_df[[
    "SEM_TRADING_SYMBOL",
    "last_price",
    "volume",
]].head())
# Buy/Sell Pressure

# Simple Strength Score
# Confidence Score (0-100)

 #Buy Pressure

merged_df["entry"] = merged_df["last_price"]

merged_df["sl"] = (merged_df["last_price"] * 0.985).round(2)

merged_df["target1"] = (merged_df["last_price"] * 1.02).round(2)

merged_df["target2"] = (merged_df["last_price"] * 1.04).round(2)

ist = timezone(timedelta(hours=5, minutes=30))
merged_df["time"] = datetime.now(ist).strftime("%I:%M %p")
scanner = merged_df.copy()
print("\nTop 10 Scanner V2")
print(scanner[[
    "SEM_TRADING_SYMBOL",
    "last_price",
    "volume"
]])
print("Merged DF:", len(merged_df))
print("Scanner DF:", len(scanner))
message = f"""
<b>🚀 V3 FINAL PRO SCANNER PREMIUM</b>

━━━━━━━━━━━━━━━━━━
📅 {datetime.now(ist).strftime('%d-%m-%Y')}
🕒 {datetime.now(ist).strftime('%I:%M %p')}
📊 Market : NSE F&O
━━━━━━━━━━━━━━━━━━

🏆 <b>TOP HIGH PROBABILITY TRADES</b>

"""

rank = 1

if send_message(message):
    print("Header sent successfully.")
else:
    print("Header failed.")

rank = 1

print(f"Scanner Count: {len(scanner)}")
scanner = scanner.sort_values("volume", ascending=False)
scanner = scanner.head(5)
for _, row in scanner.iterrows():
    print("Processing:", row["SEM_TRADING_SYMBOL"])
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=70)).strftime("%Y-%m-%d")
    print("Security ID:", row["security_id"])   
    history = get_historical_data(
        int(row["security_id"]),
        from_date,
        to_date)
   
    if history.get("status") != "success":
        print("Historical Data Error:", history)
        continue
    history_df = pd.DataFrame(history["data"])
try:
    history_df["date"] = pd.to_datetime(history_df["timestamp"], unit="s")
    history_df = history_df.set_index("date")

    weekly = history_df.resample("W").agg({
        "high": "max"
    })

    previous_week_high = weekly.iloc[-2]["high"]

except Exception as e:
    print("Weekly Error:", e)
    continue
    history_df["ema20"] = EMAIndicator(
        close=history_df["close"],
        window=20
    ).ema_indicator()

    history_df["ema50"] = EMAIndicator(
        close=history_df["close"],
        window=50
    ).ema_indicator()
    
    print(history_df[["close", "ema20", "ema50"]].tail())
    # EMA BUY / SELL Confirmation
    
last = history_df.iloc[-1]

previous_day_high = history_df.iloc[-2]["high"]

history_df = history_df.sort_index()

last_date = history_df.index[-1]

current_week = last_date.isocalendar().week
current_year = last_date.isocalendar().year
print("Last Price:", row["last_price"])
print("Previous Day High:", previous_day_high)
print("Previous Week High:", previous_week_high)

previous_week_df = history_df[
    ~(
        (history_df.index.isocalendar().week == current_week) &
        (history_df.index.isocalendar().year == current_year)
    )
]

previous_week_high = previous_week_df.tail(5)["high"].max()

buy_signal = (
    row["last_price"] > previous_day_high and
    row["last_price"] > previous_week_high
)

trade = (
        f"🏆 Rank #{rank}\n"
        f"<b>{row['SEM_TRADING_SYMBOL']}</b>\n"
        f"🎯 Signal : 🟢 BREAKOUT BUY\n"
        f"💰 Entry : ₹{row['entry']}\n"
        f"🛑 SL : ₹{row['sl']}\n"
        f"🎯 Target 1 : ₹{row['target1']}\n"
        f"🚀 Target 2 : ₹{row['target2']}\n"
        f"🕒 Time : {row['time']}")

send_message(trade)
rank += 1
print("Telegram message sent successfully.")
# Top OI Stocks

