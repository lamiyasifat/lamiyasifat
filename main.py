from datetime import datetime
import random
import time
from binance_feed import get_binance_futures_candles
from telegram_bot import send_telegram_signal

# ১ থেকে ২০ পর্যন্ত সব স্ট্র্যাটেজির ইম্পোর্ট
from strategies.strategy_1 import check_setup_1
from strategies.strategy_2 import check_setup_2
from strategies.strategy_3 import check_setup_3
from strategies.strategy_4 import check_setup_4
from strategies.strategy_5 import check_setup_5
from strategies.strategy_6 import check_setup_6
from strategies.strategy_7 import check_setup_7
from strategies.strategy_8 import check_setup_8
from strategies.strategy_9 import check_setup_9
from strategies.strategy_10 import check_setup_10
from strategies.strategy_11 import check_setup_11
from strategies.strategy_12 import check_setup_12
from strategies.strategy_13 import check_setup_13
from strategies.strategy_14 import check_setup_14
from strategies.strategy_15 import check_setup_15
from strategies.strategy_16 import check_setup_16
from strategies.strategy_17 import check_setup_17
from strategies.strategy_18 import check_setup_18
from strategies.strategy_19 import check_setup_19
from strategies.strategy_20 import check_setup_20

STRATEGY_LIST = [
    ("Setup 1", check_setup_1),
    ("Setup 2", check_setup_2),
    ("Setup 3", check_setup_3),
    ("Setup 4", check_setup_4),
    ("Setup 5", check_setup_5),
    ("Setup 6", check_setup_6),
    ("Setup 7", check_setup_7),
    ("Setup 8", check_setup_8),
    ("Setup 9", check_setup_9),
    ("Setup 10", check_setup_10),
    ("Setup 11", check_setup_11),
    ("Setup 12", check_setup_12),
    ("Setup 13", check_setup_13),
    ("Setup 14", check_setup_14),
    ("Setup 15", check_setup_15),
    ("Setup 16", check_setup_16),
    ("Setup 17", check_setup_17),
    ("Setup 18", check_setup_18),
    ("Setup 19", check_setup_19),
    ("Setup 20", check_setup_20),
]

# নিরাপদ এবং ফাস্ট স্ক্যান করার জন্য বাছাইকৃত ৩০টি ফিউচার্স পেয়ার
BINANCE_FUTURES_PAIRS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "DOT/USDT",
    "MATIC/USDT",
    "LTC/USDT",
    "BCH/USDT",
    "NEAR/USDT",
    "ATOM/USDT",
    "UNI/USDT",
    "XLM/USDT",
    "ETC/USDT",
    "RENDER/USDT",
    "INJ/USDT",
    "FET/USDT",
    "AR/USDT",
    "ICP/USDT",
    "APT/USDT",
    "OP/USDT",
    "ARB/USDT",
    "SUI/USDT",
    "TIA/USDT",
    "SEI/USDT",
    "PEPE/USDT",
]


def scan_all_strategies(df):
  for setup_name, func in STRATEGY_LIST:
    try:
      signal = func(df)
      if signal in ["CALL", "PUT"]:
        return setup_name, signal
    except Exception:
      continue
  return None, None


def start_bot():
  print("🤖 Binance Futures Automated Trading Bot Started (Without Leverage)...")
  print(
      f"📊 Monitoring {len(BINANCE_FUTURES_PAIRS)} pairs with 20 loaded"
      " strategies."
  )

  last_scanned_minute = -1

  while True:
    try:
      now = datetime.now()
      second = now.second
      minute = now.minute

      # প্রতি মিনিটের ঠিক ৫৮ সেকেন্ডে স্ক্যান করবে
      if second == 58 and minute != last_scanned_minute:
        last_scanned_minute = minute
        print(
            "\n🔍 Scanning Binance Futures Market at"
            f" {now.strftime('%H:%M:%S')}..."
        )

        for symbol in BINANCE_FUTURES_PAIRS:
          try:
            # binance_api.py থেকে ১ মিনিটের ক্যান্ডেল ডেটা ফেচ করা (লে ছাড়া)
            df = get_binance_futures_candles(symbol, timeframe="1m", limit=100)

            if df is not None and not df.empty:
              setup_name, signal = scan_all_strategies(df)
              if signal:
                print(
                    f"✅ FUTURES MATCH FOUND! [{symbol}] - {setup_name} ->"
                    f" {signal}"
                )
                # telegram_bot.py এর মাধ্যমে সিগন্যাল পাঠানো
                send_telegram_signal(symbol, setup_name, signal)

            time.sleep(random.uniform(0.2, 0.4))

          except Exception as pair_err:
            print(f"⚠️ Error scanning {symbol}: {pair_err}")

        time.sleep(3)

      time.sleep(0.5)

    except KeyboardInterrupt:
      print("\n🛑 Bot stopped manually.")
      break
    except Exception as global_err:
      print(f"⚠️ Unexpected error in main loop: {global_err}")
      time.sleep(1)


if __name__ == "__main__":
  while True:
    try:
      start_bot()
    except Exception as e:
      print(f"⚠️ Bot crashed with error: {e}. Restarting in 5 seconds...")
      time.sleep(5)
        
