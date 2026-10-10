import json
import time
import pandas as pd
import re
from collections import defaultdict
from curl_cffi import requests
from config import QUOTEX_EMAIL, QUOTEX_PASSWORD

OTC_PAIRS = [
    "NZD/JPY (OTC)", "USD/PHP (OTC)", "USD/IDR (OTC)", "USD/MXN (OTC)", "USD/BRL (OTC)",
    "USD/COP (OTC)", "USD/INR (OTC)", "USD/DZD (OTC)", "GBP/NZD (OTC)", "USD/ZAR (OTC)",
    "USD/ARS (OTC)", "USD/BDT (OTC)", "USD/NGN (OTC)", "NZD/CAD (OTC)", "USD/CHF (OTC)",
    "USD/EGP (OTC)", "USD/PKR (OTC)", "NZD/USD (OTC)", "EUR/NZD (OTC)", "AUD/NZD (OTC)"
]

market_data = defaultdict(list)

def get_pair_df(pair):
    if pair in market_data and len(market_data[pair]) > 0:
        return pd.DataFrame(market_data[pair])
    return pd.DataFrame()

def start_websocket():
    print("🌐 Authenticating via Chrome 120 impersonation (Polling Mode)...")
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://qxbroker.com",
        "Referer": "https://qxbroker.com/"
    }
    
    try:
        session.get("https://qxbroker.com/en", headers=headers, timeout=15)
        login_res = session.post(
            "https://qxbroker.com/api/v1/auth/login", 
            json={"email": QUOTEX_EMAIL, "password": QUOTEX_PASSWORD}, 
            headers=headers, 
            timeout=30
        )
        
        if login_res.status_code != 200:
            print(f"❌ Login failed: {login_res.text}")
            return
            
        poll_url = "https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling"
        poll_res = session.get(poll_url, headers=headers, timeout=15)
        
        if poll_res.status_code == 200:
            match = re.search(r'"sid":"([^"]+)"', poll_res.text) or re.search(r'\\"sid\\":\\"([^\\"]+)\\"', poll_res.text)
            if not match:
                print("❌ Could not parse SID.")
                return
            
            sid = match.group(1)
            print(f"✅ Polling Session Connected! SID: {sid}")
            
            for pair in OTC_PAIRS:
                sub_msg = f'42["s_subscribe", {{"asset": "{pair}", "period": 60}}]'
                packet = f"{len(sub_msg)}:{sub_msg}"
                session.post(f"https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling&sid={sid}", data=packet, headers=headers, timeout=15)
                time.sleep(0.05)
            
            print(f"🚀 Subscribed to {len(OTC_PAIRS)} Pairs via Polling...\n")
            
            while True:
                try:
                    res = session.get(f"https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling&sid={sid}", headers=headers, timeout=15)
                    if res.status_code == 200:
                        text = res.text
                        if text and text != '3':
                            if '42' in text:
                                parts = text.split('42')
                                for part in parts[1:]:
                                    try:
                                        start_idx = part.find('[')
                                        if start_idx != -1:
                                            data = json.loads(part[start_idx:])
                                            if isinstance(data, list) and len(data) > 1:
                                                payload = data[1]
                                                items = payload if isinstance(payload, list) else [payload]
                                                for item in items:
                                                    if isinstance(item, dict):
                                                        asset = item.get("asset") or item.get("symbol")
                                                        if asset in OTC_PAIRS:
                                                            open_val = float(item.get("open", 0))
                                                            close_val = float(item.get("close", 0))
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
                                    except Exception:
                                        pass
                    time.sleep(1)
                except Exception as loop_e:
                    print(f"⚠️ Polling loop error: {loop_e}")
                    time.sleep(2)
        else:
            print("❌ Polling Handshake Failed.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_websocket()
        
