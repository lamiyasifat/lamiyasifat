import websocket
import json
import time
import ssl
from playwright.sync_api import sync_playwright
from config import QUOTEX_EMAIL, QUOTEX_PASSWORD

# ২০টি লাইভ OTC পেয়ার
OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc",
    "NZDUSD_otc", "EURCAD_otc", "EURAUD_otc", "GBPCAD_otc", "GBPAUD_otc",
    "USDIDR_otc", "USDBRL_otc", "USDINR_otc", "UKBrent_otc", "USCrude_otc"
]

def get_playwright_session():
    """Playwright ব্যবহার করে অটো-লগইন করে কুকি এবং ইউজার এজেন্ট সংগ্রহ করবে"""
    print("🌐 Launching Playwright to get session cookies...")
    with sync_playwright() as p:
        # ব্যাকগ্রাউন্ডে ব্রাউজার রান করার জন্য headless=True ব্যবহার করা হয়েছে
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # Quotex লগইন পেজে যাওয়া (Timeout ৬০ সেকেন্ড করা হলো)
            page.goto("https://qxbroker.com/en/sign-in", timeout=60000)
            
            # ইমেইল ইনপুট করা (Timeout ৬০ সেকেন্ড করা হলো যাতে লোড হওয়ার পর্যাপ্ত সময় পায়)
            page.wait_for_selector('input[name="email"]', timeout=60000)
            page.fill('input[name="email"]', QUOTEX_EMAIL)
            
            # পাসওয়ার্ড ইনপুট করা
            page.fill('input[name="password"]', QUOTEX_PASSWORD)
            
            # লগইন বাটনে ক্লিক করা
            page.click('button[type="submit"]')
            print("⏳ Logging in via Playwright...")
            
            # লগইন সম্পন্ন হওয়ার জন্য অপেক্ষা করা
            time.sleep(10)
            
            # কুকি সংগ্রহ করা
            cookies = context.cookies("https://qxbroker.com")
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            
            user_agent = page.evaluate("navigator.userAgent")
            
            browser.close()
            print("✅ Successfully acquired session cookies via Playwright!")
            return cookie_str, user_agent
            
        except Exception as e:
            print(f"❌ Playwright login error: {e}")
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
                print(f"│ 📈 [{pair}] ─── Price: {price}")
                
        except Exception:
            pass
            
    elif message == '2':
        # কানেকশন সক্রিয় রাখতে Ping-Pong Response
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
    # প্লে-রাইটের মাধ্যমে ডায়নামিক কুকি এবং ইউজার এজেন্ট নেওয়া
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

if __name__ == "__main__":
    start_websocket()
