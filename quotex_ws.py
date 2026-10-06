import json
import time
import ssl
import websocket
from curl_cffi import requests
from config import QUOTEX_EMAIL, QUOTEX_PASSWORD

# ২০টি লাইভ OTC পেয়ার
OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc",
    "NZDUSD_otc", "EURCAD_otc", "EURAUD_otc", "GBPCAD_otc", "GBPAUD_otc",
    "USDIDR_otc", "USDBRL_otc", "USDINR_otc", "UKBrent_otc", "USCrude_otc"
]

def get_session_via_api():
    """TLS ফিঙ্গারপ্রিন্ট ইমপারসনেশন ব্যবহার করে ব্রাউজার ও কুকিজ ছাড়াই সরাসরি সেশন তৈরি করবে"""
    print("🌐 Connecting via TLS Fingerprint Impersonation (No Browser)...")
    
    # আসল ক্রোম ব্রাউজারের ফিঙ্গারপ্রিন্ট নকল করা
    session = requests.Session(impersonate="chrome120")
    
    login_url = "https://qxbroker.com/en/sign-in"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        # ক্লাউডফ্লেয়ার চ্যালেঞ্জ পার করতে সাইন-ইন পেজে রিকোয়েস্ট পাঠানো
        response = session.get(login_url, headers=headers, timeout=30)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 403:
            print("❌ Cloudflare blocked the connection.")
            return None, None

        # সেশনের কুকিজ ও ইউজার এজেন্ট সংগ্রহ করা
        cookie_dict = session.cookies.get_dict()
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        print("✅ API Session established successfully without browser!")
        return cookie_str, user_agent
        
    except Exception as e:
        print(f"❌ API Connection error: {e}")
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
                # print(f"│ 📈 [{pair}] ─── Price: {price}")
                
        except Exception:
            pass
            
    elif message == '2':
        ws.send('3')

def on_open(ws):
    print("✅ Connected to Quotex WebSocket via API Session!\n")
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
    cookie_str, user_agent = get_session_via_api()
    
    if not cookie_str:
        print("❌ Failed to establish session. Retrying in 10 seconds...")
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
        
