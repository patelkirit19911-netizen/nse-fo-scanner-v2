from market_data import get_nifty_stocks, get_live_quotes, get_historical_data
import ta
import pandas as pd
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
from telegram import send_message, send_photo
from datetime import datetime, timedelta, timezone
import dhanhq
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
print(dhanhq.__file__)
sent_signals = set()
def create_chart(df, symbol):
    df = df.copy()

    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })

    filename = f"{symbol}.png"

    mpf.plot(
        df,
        type="candle",
        volume=True,
        style="yahoo",
        savefig=filename
    )

    return filename
print("Loading NIFTY100 Stocks...")

stocks = get_nifty_stocks()
print(f"Loaded {len(stocks)} NIFTY Stocks")

print("Getting Live Quotes...")
security_ids = stocks["SEM_SMST_SECURITY_ID"].astype(int).tolist()
print("Security IDs:", security_ids[:10])
print("Type:", type(security_ids))
quotes = get_live_quotes(security_ids[:1000])
if not quotes["data"]["NSE_EQ"]:
    print("No live quote data received")
    exit()
rows = []
for security_id, data in quotes["data"]["NSE_EQ"].items():
    rows.append({
        "security_id": int(security_id),
        "last_price": data.get("last_price", 0),
        "volume": data.get("volume", 0),
        "buy_qty": data.get("buy_quantity", 0),
        "sell_qty": data.get("sell_quantity", 0)
    })

live_df = pd.DataFrame(rows)

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
]].head())


#merged_df["entry"] = merged_df["last_price"]
merged_df["entry"] = 0.0
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
current_time = datetime.now(ist).time()


for _, row in scanner.iterrows():
    if row["last_price"] <= 0:
        continue
    print("Processing:", row["SEM_TRADING_SYMBOL"])
    print("ROW SYMBOL =", repr(row["SEM_TRADING_SYMBOL"]))
    print("SECURITY ID =", row["security_id"])
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    print("Security ID:", row["security_id"])   
    history = get_historical_data(int(row["security_id"]),from_date,to_date)
    print("History Status =", history.get("status"))
    #print(type(history))
    #print(history.keys())
    #print(history["data"].keys())
    if history.get("status") != "success":
        print("Historical Data Error:", history)
        continue
    history_df = pd.DataFrame.from_dict(history["data"])
    print("History DF Length:", len(history_df))
    print("Reached after history_df")
    print("Before last row")
    print("TYPE =", type(row["SEM_TRADING_SYMBOL"]))
    print("VALUE =", row["SEM_TRADING_SYMBOL"])
    print("EQUAL =", row["SEM_TRADING_SYMBOL"].strip() == "HDFCBANK")
    last = history_df.iloc[-1]
    print("DEBUG 2")
    
    history_df["date"] = pd.to_datetime(history_df["timestamp"], unit="s", utc=True)
    history_df["date"] = history_df["date"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    history_df = history_df.set_index("date")
    history_df = history_df.sort_index()

    last_date = history_df.index[-1]
    print("Last Date:", last_date)
    print(history_df.index[-5:])
    current_week = last_date.isocalendar().week
    current_year = last_date.isocalendar().year
    previous_week = current_week - 1
    previous_week_year = current_year

    if previous_week == 0:
        previous_week = 52
        previous_week_year -= 1
    print("Last Price:", row["last_price"])


    previous_week_df = history_df[
    (history_df.index.isocalendar().week == previous_week) &
    (history_df.index.isocalendar().year == previous_week_year)]

    previous_week_high = previous_week_df["high"].max()
    if previous_week_df.empty:
        print("Previous week data not found")
        continue
    print("Previous Week High:", previous_week_high)
    print("Symbol:", row["SEM_TRADING_SYMBOL"])
    print("Last Price:", row["last_price"])

    today_df = history_df[
    (history_df.index.date == last_date.date()) &
    (
        (history_df.index.hour > 9) |
        ((history_df.index.hour == 9) & (history_df.index.minute >= 15))
    )
    ]
    if today_df.empty:
        print("Today data not found")
        continue
    print("Today DF:", len(today_df))
    print("Today DF Length:", len(today_df))
    print(today_df.columns.tolist())
    print("Previous Week High:", previous_week_high)
    print("Today's High:", today_df["high"].max())
    print("Today's Close:", today_df["close"].max())
    today_5m = (
    today_df
    .resample("5min")
    .agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })
    .dropna()
    )

    breakout_candle = today_5m[
    (today_5m["close"].shift(1) <= previous_week_high) &
    (today_5m["close"] > previous_week_high)
    ]

    buy_signal = not breakout_candle.empty
    print("Previous Week High:", previous_week_high)
    print(row["SEM_TRADING_SYMBOL"], previous_week_high, len(breakout_candle))
    print("Buy Signal:", buy_signal)
    
    signal_key = (row["SEM_TRADING_SYMBOL"],last_date.strftime("%Y-%m-%d"))
    
    if not buy_signal or signal_key in sent_signals:
       pass
    else:
        sent_signals.add(signal_key)
        row["entry"] = previous_week_high
        trade = (
        f"🏆 Rank #{rank}\n"
        f"<b>{row['SEM_TRADING_SYMBOL']}</b>\n"
        f"🎯 Signal : 🟢 BREAKOUT BUY\n"
        f"💰 Entry : ₹{row['entry']}\n"
        f"🛑 SL : ₹{row['sl']}\n"
        f"🎯 Target 1 : ₹{row['target1']}\n"
        f"🚀 Target 2 : ₹{row['target2']}\n"
        f"🕒 Time : {row['time']}")

        chart_file = create_chart(history_df, row["SEM_TRADING_SYMBOL"])
        send_photo(chart_file, trade)
        os.remove(chart_file)
        print("Completed:", row["SEM_TRADING_SYMBOL"])
        rank += 1
        print("Telegram message sent successfully.")
print("Scanner loop completed")

