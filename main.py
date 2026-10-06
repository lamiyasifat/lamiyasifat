import time
import json
import random
import threading
from datetime import datetime

# quotex_ws.py theke websocket ba data fetch function import korben
from quotex_ws import start_websocket, OTC_PAIRS

# Telegram ebong 12-ti strategy import (Apnar github folder structure anujayi)
from telegram_bot import send_telegram_signal
from strategies.strategy_1 import QuotexStrategy1
from strategies.strategy_2 import QuotexStrategy2
from strategies.strategy_3 import QuotexStrategy3
from strategies.strategy_4 import QuotexStrategy4
from strategies.strategy_5 import QuotexStrategy5
from strategies.strategy_6 import QuotexStrategy6
from strategies.strategy_7 import QuotexStrategy7
from strategies.strategy_8 import QuotexStrategy8
from strategies.strategy_9 import QuotexStrategy9
from strategies.strategy_10 import QuotexStrategy10
from strategies.strategy_11 import QuotexStrategy11
from strategies.strategy_12 import QuotexStrategy12

STRATEGY_LIST = [
    ("Strategy 1", QuotexStrategy1()),
    ("Strategy 2", QuotexStrategy2()),
    ("Strategy 3", QuotexStrategy3()),
    ("Strategy 4", QuotexStrategy4()),
    ("Strategy 5", QuotexStrategy5()),
    ("Strategy 6", QuotexStrategy6()),
    ("Strategy 7", QuotexStrategy7()),
    ("Strategy 8", QuotexStrategy8()),
    ("Strategy 9", QuotexStrategy9()),
    ("Strategy 10", QuotexStrategy10()),
    ("Strategy 11", QuotexStrategy11()),
    ("Strategy 12", QuotexStrategy12()),
]

def scan_all_strategies(df):
    """Candle data check kore 12-ti strategy test korbe"""
    try:
        last_candle_color = df.iloc[-1]['color'] if 'color' in df.columns else 'RED'
    except Exception:
        last_candle_color = 'RED'

    for setup_name, strat_obj in STRATEGY_LIST:
        try:
            signal, step = strat_obj.analyze_candle(last_candle_color)
            if signal and signal in ["GREEN", "RED"]:
                return setup_name, signal
        except Exception:
            continue
    return None, None

def start_bot():
    print("🤖 Quotex OTC Telegram Signal Bot Started...")

    # Background-e Quotex WebSocket (TLS API session) chalu kora
    ws_thread = threading.Thread(target=start_websocket)
    ws_thread.daemon = True
    ws_thread.start()

    time.sleep(5)  # Connection stable howa porjonto oppikkha
    last_scanned_minute = -1

    while True:
        try:
            now = datetime.now()
            second = now.second
            minute = now.minute

            # Proti minute-er 58 second-e scan hobe
            if second == 58 and minute != last_scanned_minute:
                last_scanned_minute = minute
                print(f"\n🔍 Scanning Market at {now.strftime('%H:%M:%S')}...")

                for pair in OTC_PAIRS:
                    try:
                        # Pair-er candle data niye asar function 
                        df = globals().get("get_pair_df", lambda p: None)(pair)

                        if df is not None and not df.empty:
                            setup_name, signal = scan_all_strategies(df)
                            if signal:
                                print(f"✅ MATCH FOUND! [{pair}] - {setup_name} -> {signal}")

                                # Telegram-e signal pathano
                                send_telegram_signal(pair, setup_name, signal)

                        time.sleep(random.uniform(0.05, 0.1))

                    except Exception as pair_err:
                        print(f"⚠️ Error scanning {pair}: {pair_err}")

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
            
