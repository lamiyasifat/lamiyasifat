import time
import json
import random
import threading
from datetime import datetime

# quotex_ws.py theke websocket ba data fetch function import korben
from quotex_ws import start_websocket, OTC_PAIRS

# Telegram ebong 20-ti strategy import
from telegram_bot import send_telegram_signal
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

def scan_all_strategies(df):
    """Candle data check kore 20-ti strategy test korbe"""
    for setup_name, func in STRATEGY_LIST:
        try:
            res = func(df)
            if res and isinstance(res, tuple):
                signal, desc = res
                if signal in ["CALL", "PUT"]:
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
                        # (Jeta quotex_ws theke global ba store theke ashbe)
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
