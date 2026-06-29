from market_data import get_fno_stocks
from strategy import filter_stocks
from telegram import send_message

print("Loading NSE F&O Stocks...")

stocks = get_fno_stocks()

filtered = filter_stocks(stocks)

print(f"Loaded {len(filtered)} F&O Stocks")

send_message(
    f"✅ Scanner V2 Running\nF&O Stocks Loaded: {len(filtered)}"
)
