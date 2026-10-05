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
    """Playwright Stealth এবং হেভি অ্যান্টি-বট আর্গুমেন্ট দিয়ে VPS থেকে লগইন করবে"""
    print("🌐 Launching VPS Browser to bypass Cloudflare...")
    with sync_playwright() as p:
        # ক্লাউডফ্লেয়ার ডিটেকশন এড়ানোর জন্য ব্রাউজার আর্গুমেন্ট
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--start-maximized"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False
        )
        
        # বট ট্রেস লুকাতে এক্সট্রা জাভাস্ক্রিপ্ট ওভাররাইড
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        try:
            print("⏳ Navigating to Quotex sign-in page...")
            # পেজ রেন্ডার হওয়ার জন্য রিলায়েবল মোড
            page.goto("https://qxbroker.com/en/sign-in", timeout=60000, wait_until="domcontentloaded")
            
            # ইমেইল ইনপুট ফিল্ড আসার জন্য পর্যাপ্ত সময় দেওয়া
            print("✍️ Waiting for login fields...")
            page.wait_for_selector('input[name="email"]', timeout=60000)
            
            print("✍️ Entering credentials...")
            page.fill('input[name="email"]', QUOTEX_EMAIL)
            page.fill('input[name="password"]', QUOTEX_PASSWORD)
            
            # হিউম্যান বিহেভিওরের মতো সামান্য বিরতি
            time.sleep(2)
            page.click('button[type="submit"]')
            print("⏳ Logging in, waiting for dashboard...")
            
            # ড্যাশবোর্ড লোড হওয়ার জন্য অপেক্ষা
            time.sleep(15)
            
            cookies = context.cookies("https://qxbroker.com")
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            user_agent = page.evaluate("navigator.userAgent")
            
            browser.close()
            print("✅ Successfully logged in via VPS and acquired session!")
            return cookie_str, user_agent
            
        except Exception as e:
            print(f"❌ Login error: {e}")
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

if __name__ == "__main__":
    start_websocket()
    
