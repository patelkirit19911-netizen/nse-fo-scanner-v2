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
merged_df["buy_sell_ratio"] = (
    merged_df["buy_qty"] / (merged_df["sell_qty"] + 1)
)

# Simple Strength Score
# Confidence Score (0-100)

merged_df["score"] = 0
 #V3 Pro Confidence Score

#Price above VWAP
merged_df.loc[merged_df["last_price"] > merged_df["vwap"], "score"] += 20

 #EMA Trend
 #EMA Trend Score
#merged_df.loc[
   # merged_df["last_price"] > merged_df["ema20"],
   # "score"
#] += 20


 #Volume Strength
merged_df["vol_rank"] = merged_df["volume"].rank(pct=True)
merged_df.loc[merged_df["vol_rank"] >= 0.80, "score"] += 20

 #Buy Pressure
merged_df.loc[merged_df["buy_sell_ratio"] > 1.20, "score"] += 20

merged_df["entry"] = merged_df["last_price"]

merged_df["sl"] = (merged_df["last_price"] * 0.985).round(2)

merged_df["target1"] = (merged_df["last_price"] * 1.02).round(2)

merged_df["target2"] = (merged_df["last_price"] * 1.04).round(2)

ist = timezone(timedelta(hours=5, minutes=30))
merged_df["time"] = datetime.now(ist).strftime("%I:%M %p")
print(merged_df[["SEM_TRADING_SYMBOL", "score"]].sort_values("score", ascending=False).head(20))
scanner = merged_df.sort_values("score", ascending=False).head(15)
print("\nTop 10 Scanner V2")
print(scanner[[
    "SEM_TRADING_SYMBOL",
    "last_price",
    "volume",
    "buy_sell_ratio"
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
print("Scanner Count:", len(scanner))
print(scanner[["SEM_TRADING_SYMBOL", "score"]])
print(scanner.head())

for _, row in scanner.iterrows():
    print("Processing:", row["SEM_TRADING_SYMBOL"])
    to_date = datetime.now().strftime("%Y-%m-%d")
from_date = (datetime.now() - timedelta(days=70)).strftime("%Y-%m-%d")
    print("Security ID:", row["security_id"])   
    history = get_historical_data(
        int(row["security_id"]),
        from_date,
        to_date
    )
    # print(history)
    if history.get("status") != "success":
        print("Historical Data Error:", history)
        continue

    history_df = pd.DataFrame(history["data"])

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
highest_high = history_df.iloc[-6:-1]["high"].max()
avg_volume = history_df.iloc[-6:-1]["volume"].mean()
    buy_signal = (
    last["ema20"] > last["ema50"] and
    row["last_price"] > highest_high * 1.002 and
    row["last_price"] > row["vwap"] and
    last["volume"] > avg_volume
)
  if not buy_signal:
    continue

signal = "🟢 BREAKOUT BUY"  
score = int(row["score"])
    if last["ema20"] > last["ema50"]:
        score += 20
    if last["close"] > last["ema20"]:
        score += 20

    trade = (
        f"🏆 Rank #{rank}\n"
        f"<b>{row['SEM_TRADING_SYMBOL']}</b>\n"
        f"⭐ Confidence : {score}/100\n"
        f"📢 Signal : {signal}\n"
        f"💰 Entry : ₹{row['entry']}\n"
        f"🛑 SL : ₹{row['sl']}\n"
        f"🎯 Target 1 : ₹{row['target1']}\n"
        f"🚀 Target 2 : ₹{row['target2']}\n"
        f"📊 Volume : {row['volume']}\n"
        f"🕒 Time : {row['time']}"
    )

    send_message(trade)
    rank += 1
print("Telegram message sent successfully.")
# Top OI Stocks

