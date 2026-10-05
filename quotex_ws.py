import websocket
import json
import time
import ssl
from config import COOKIE, USER_AGENT

# ২০টি লাইভ OTC পেয়ার
OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc",
    "NZDUSD_otc", "EURCAD_otc", "EURAUD_otc", "GBPCAD_otc", "GBPAUD_otc",
    "USDIDR_otc", "USDBRL_otc", "USDINR_otc", "UKBrent_otc", "USCrude_otc"
]

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
    ws_url = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"

    headers = {
        "User-Agent": USER_AGENT,
        "Cookie": COOKIE,
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
  
