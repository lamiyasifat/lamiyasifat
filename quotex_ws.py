import json
import time
import ssl
import websocket
import pandas as pd
from collections import defaultdict
from curl_cffi import requests
from config import QUOTEX_EMAIL, QUOTEX_PASSWORD

OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc",
    "NZDUSD_otc", "EURCAD_otc", "EURAUD_otc", "GBPCAD_otc", "GBPAUD_otc",
    "USDIDR_otc", "USDBRL_otc", "USDINR_otc", "UKBrent_otc", "USCrude_otc"
]

# Proti pair-er candle data store korar jonno dictionary
market_data = defaultdict(list)

def get_pair_df(pair):
    """Main.py theke call korle ei function candle data dataframe hisebe dibe"""
    if pair in market_data and len(market_data[pair]) > 0:
        df = pd.DataFrame(market_data[pair])
        return df
    return pd.DataFrame()

def get_token_without_cookies():
    print("🌐 Authenticating via Direct API...")
    session = requests.Session(impersonate="chrome120")
    try:
        response = session.post("https://qxbroker.com/api/v1/auth/login", json={"email": QUOTEX_EMAIL, "password": QUOTEX_PASSWORD}, timeout=30)
        if response.status_code == 200:
            cookie_dict = session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
            print("✅ Successfully authenticated!")
            return cookie_str, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def on_open(ws):
    print("✅ Connected to Quotex WebSocket!\n")
    for pair in OTC_PAIRS:
        ws.send(f'42["asset/subscribe", {{"asset": "{pair}"}}]')
        time.sleep(0.1)
    print(f"🚀 Scanning {len(OTC_PAIRS)} OTC Pairs...\n")

def on_message(ws, message):
    if message == '2':
        ws.send('3')
        return
    
    try:
        if message.startswith("42"):
            data = json.loads(message[2:])
            if isinstance(data, list) and len(data) > 1:
                event_name = data[0]
                payload = data[1]
                
                # Payload jodi list ba dictionary hoy, amra asset khuje ber korbo
                items = payload if isinstance(payload, list) else [payload]
                for item in items:
                    if isinstance(item, dict):
                        asset = item.get("asset") or item.get("symbol")
                        if asset in OTC_PAIRS:
                            candle = {
                                "time": item.get("time", time.time()),
                                "open": float(item.get("open", 0)),
                                "high": float(item.get("high", 0)),
                                "low": float(item.get("low", 0)),
                                "close": float(item.get("close", 0))
                            }
                            market_data[asset].append(candle)
                            
                            # লাইভ ডেটা আসার বিষয়টি টার্মিনালে দেখার জন্য প্রিন্ট যোগ করা হলো
                            print(f"📥 Received Candle for {asset}: Close={candle['close']}")

                            # Maximum 100 ti candle store kore memory clean rakha hobe
                            if len(market_data[asset]) > 100:
                                market_data[asset].pop(0)
    except Exception as e:
        pass

def start_websocket():
    cookie_str, user_agent = get_token_without_cookies()
    if not cookie_str:
        time.sleep(10)
        return
    ws = websocket.WebSocketApp(
        "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket",
        header={"User-Agent": user_agent, "Cookie": cookie_str, "Origin": "https://qxbroker.com"},
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    start_websocket()
            
