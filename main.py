import time
import json
import ssl
import random
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from config import QUOTEX_EMAIL, QUOTEX_PASSWORD

# টেলিগ্রাম এবং স্ট্র্যাটেজি ইম্পোর্ট
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

# ২০টি লাইভ OTC পেয়ার
OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc",
    "NZDUSD_otc", "EURCAD_otc", "EURAUD_otc", "GBPCAD_otc", "GBPAUD_otc",
    "USDIDR_otc", "USDBRL_otc", "USDINR_otc", "UKBrent_otc", "USCrude_otc"
]

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

def get_playwright_session():
    """Playwright Stealth ব্যবহার করে ক্লাউডফ্লেয়ার বাইপাস করে অটো-লগইন করবে"""
    print("🌐 Launching Stealth Browser to bypass Cloudflare...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        stealth_sync(page)  # Cloudflare ব্লক এড়ানোর জন্য Stealth ব্যবহার করা হয়েছে
        
        try:
            print("⏳ Navigating to Quotex sign-in page...")
            page.goto("https://qxbroker.com/en/sign-in", timeout=60000)
            
            page.wait_for_selector('input[name="email"]', timeout=60000)
            print("✍️ Entering credentials...")
            page.fill('input[name="email"]', QUOTEX_EMAIL)
            page.fill('input[name="password"]', QUOTEX_PASSWORD)
            
            page.click('button[type="submit"]')
            print("⏳ Logging in, waiting for dashboard...")
            
            time.sleep(15)
            
            cookies = context.cookies("https://qxbroker.com")
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            user_agent = page.evaluate("navigator.userAgent")
            
            browser.close()
            print("✅ Successfully acquired session cookies with Stealth!")
            return cookie_str, user_agent
            
        except Exception as e:
            print(f"❌ Playwright Stealth login error: {e}")
            browser.close()
            return None, None

def on_message(ws, message):
    if message.startswith('42'):
        try:
            data = json.loads(message[2:])
            event_name = data[0]
            
            if event_name in ["live", "history"]:
                payload = data[1]
                pair = payload.get("asset", "Unknown")
                price = payload.get("price", payload.get("close", "N/A"))
                # চাইলে এখানে প্রাইস প্রিন্ট দেখতে পারেন অথবা কমেন্ট করে রাখতে পারেন
                # print(f"│ 📈 [{pair}] ─── Price: {price}")
                
        except Exception:
            pass
            
    elif message == '2':
        ws.send('3')

def on_open(ws):
    print("✅ Connected to Quotex WebSocket!\n")
    for pair in OTC_PAIRS:
        subscribe_msg = f'42["asset/subscribe", {{"asset": "{pair}"}}]'
        ws.send(subscribe_msg)
        time.sleep(0.1)
    print(f"🚀 Scanning {len(OTC_PAIRS)} OTC Pairs Live...\n")

def on_error(ws, error):
    print(f"❌ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("⚠️ WebSocket Connection Closed")

def start_websocket():
    cookie_str, user_agent = get_playwright_session()
    
    if not cookie_str:
        print("❌ Failed to get session cookies. Retrying in 10 seconds...")
        time.sleep(10)
        return

    ws_url = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"

    headers = {
        "User-Agent": user_agent,
        "Cookie": cookie_str,
        "Origin": "https://qxbroker.com"
    }

    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def scan_all_strategies(df):
    """ক্যান্ডেল ডাটা চেক করে ২০টি স্ট্র্যাটেজি টেস্ট করবে"""
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

    # ব্যাকগ্রাউন্ডে Quotex WebSocket চালু করা
    ws_thread = threading.Thread(target=start_websocket)
    ws_thread.daemon = True
    ws_thread.start()

    time.sleep(5)  # কানেকশন স্ট্যাবল হওয়া পর্যন্ত অপেক্ষা
    last_scanned_minute = -1

    while True:
        try:
            now = datetime.now()
            second = now.second
            minute = now.minute

            # প্রতি মিনিটের ৫৮ সেকেন্ডে স্ক্যান হবে
            if second == 58 and minute != last_scanned_minute:
                last_scanned_minute = minute
                print(f"\n🔍 Scanning Market at {now.strftime('%H:%M:%S')}...")

                for pair in OTC_PAIRS:
                    try:
                        # পেয়ারের ক্যান্ডেল ডাটা নেওয়ার ফাংশন (প্রয়োজন অনুযায়ী মডিফাইড)
                        df = globals().get("get_pair_df", lambda p: None)(pair)

                        if df is not None and not df.empty:
                            setup_name, signal = scan_all_strategies(df)
                            if signal:
                                print(f"✅ MATCH FOUND! [{pair}] - {setup_name} -> {signal}")

                                # টেলিগ্রামে সিগন্যাল ও রেজাল্ট ট্র্যাকার পাঠানো
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
            
