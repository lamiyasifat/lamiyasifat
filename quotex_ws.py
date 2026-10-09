import json
import time
import ssl
import websocket
import pandas as pd
from collections import defaultdict
from curl_cffi import requests
from config import QUOTEX_EMAIL, QUOTEX_PASSWORD

OTC_PAIRS = [
    "NZD/JPY (OTC)", "USD/PHP (OTC)", "USD/IDR (OTC)", "USD/MXN (OTC)", "USD/BRL (OTC)",
    "USD/COP (OTC)", "USD/INR (OTC)", "USD/DZD (OTC)", "GBP/NZD (OTC)", "USD/ZAR (OTC)",
    "USD/ARS (OTC)", "USD/BDT (OTC)", "USD/NGN (OTC)", "NZD/CAD (OTC)", "NZD/CHF (OTC)",
    "USD/EGP (OTC)", "USD/PKR (OTC)", "NZD/USD (OTC)", "EUR/NZD (OTC)", "AUD/NZD (OTC)"
]

market_data = defaultdict(list)

def get_pair_df(pair):
    if pair in market_data and len(market_data[pair]) > 0:
        df = pd.DataFrame(market_data[pair])
        return df
    return pd.DataFrame()

def get_session_and_token():
    print("🌐 Authenticating and getting Socket Session via Direct API...")
    session = requests.Session(impersonate="chrome120")
    try:
        response = session.post("https://qxbroker.com/api/v1/auth/login", json={"email": QUOTEX_EMAIL, "password": QUOTEX_PASSWORD}, timeout=30)
        if response.status_code == 200:
            cookie_dict = session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
            
            poll_resp = session.get("https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling", timeout=15)
            if poll_resp.status_code == 200:
                raw_text = poll_resp.text
                
                import re
                match = re.search(r'\\"sid\\":\\"([^\\"]+)\\"', raw_text)
                if not match:
                    match = re.search(r'"sid":"([^"]+)"', raw_text)
                
                if match:
                    sid = match.group(1)
                    print(f"✅ Successfully authenticated & Got Socket Session ID!")
                    return cookie_str, sid, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            print("❌ Failed to parse Socket.io session ID.")
            return None, None, None
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None

def on_open(ws):
    print("✅ Connected to Quotex WebSocket!\n")
    for pair in OTC_PAIRS:
        ws.send(f'42["s_subscribe", {{"asset": "{pair}", "period": 60}}]')
        time.sleep(0.05)
    print(f"🚀 Subscribed to {len(OTC_PAIRS)} OTC Pairs...\n")

def on_message(ws, message):
    if message == '2':
        ws.send('3')
        return
    
    try:
        if message.startswith("42"):
            data = json.loads(message[2:])
            if isinstance(data, list) and len(data) > 1:
                payload = data[1]
                items = payload if isinstance(payload, list) else [payload]
                for item in items:
                    if isinstance(item, dict):
                        asset = item.get("asset") or item.get("symbol")
                        if asset in OTC_PAIRS:
                            open_val = float(item.get("open", 0))
                            close_val = float(item.get("close", 0))
                            
                            # Strategy-gula 'color' khoje, tai ekhane automatic color generate kore dewa holo
                            color = "GREEN" if close_val >= open_val else "RED"
                            
                            candle = {
                                "time": item.get("time", time.time()),
                                "open": open_val,
                                "high": float(item.get("high", 0)),
                                "low": float(item.get("low", 0)),
                                "close": close_val,
                                "color": color
                            }
                            market_data[asset].append(candle)
                            
                            if len(market_data[asset]) > 100:
                                market_data[asset].pop(0)

                            print(f"📥 Live Update -> {asset} | Close: {close_val} | Color: {color}")
    except Exception as e:
        pass

def on_error(ws, error):
    print(f"❌ WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 WebSocket Closed: {close_status_code} - {close_msg}")

def start_websocket():
    cookie_str, sid, user_agent = get_session_and_token()
    if not cookie_str or not sid:
        time.sleep(10)
        return
    
    ws_url = f"wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket&sid={sid}"
    ws = websocket.WebSocketApp(
        ws_url,
        header={
            "User-Agent": user_agent, 
            "Cookie": cookie_str, 
            "Origin": "https://qxbroker.com",
            "Referer": "https://qxbroker.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        },
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    start_websocket()
        
