import os
import threading
import time
import requests
from quotex_ws import get_pair_df

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8569676842:AAE18dypxuwl57uU_GTKRyhJBrhHP_YslDQ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6885238220")

completed_results = []
results_lock = threading.Lock()
BATCH_SIZE = 20

def send_telegram_signal(pair, setup_name, signal_type, martingale_step=1):
    """Signal ebong Martingale Step telegram-e pathabe"""
    signal_upper = str(signal_type).upper()
    
    # GREEN/CALL অথবা RED/PUT উভয় ফরম্যাটের জন্যই ইমোজি হ্যান্ডেল করা হলো
    if signal_upper in ["GREEN", "CALL"]:
        emoji = "🟢 CALL (BUY)"
    else:
        emoji = "🔴 PUT (SELL)"
    
    # Jodi step 1 er beshi hoy, tahole message-e Martingale step show korbe
    step_info = f"⚡ **Martingale Step:** `{martingale_step}`\n" if martingale_step > 1 else ""
    
    message = (
        f"🚨 **QUOTEX OTC SIGNAL (1M)** 🚨\n\n"
        f"📊 **Pair:** `{pair}`\n"
        f"🎯 **Strategy:** `{setup_name}`\n"
        f"{step_info}"
        f"⚡ **Direction:** {emoji}\n"
        f"⏱ **Timeframe:** 1 Minute\n\n"
        f"⚠️ *00:00 সেকেন্ডে এন্ট্রি নিন!*"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            t = threading.Thread(target=track_quotex_result, args=(pair, setup_name, signal_type))
            t.daemon = True
            t.start()
        else:
            print(f"Telegram Send Error: {response.text}")
    except Exception as e:
        print(f"Telegram Alert Error: {e}")

def track_quotex_result(pair, setup_name, signal_type):
    time.sleep(60)
    try:
        df = get_pair_df(pair)
        if not df.empty and len(df) >= 2:
            last_candle = df.iloc[-2]
            open_price = float(last_candle["open"])
            close_price = float(last_candle["close"])
            
            actual_result = "CALL" if close_price > open_price else "PUT"
            res_status = "WIN" if actual_result == signal_type else "LOSS"
            
            result_msg = (
                f"✅ **QUOTEX RESULT: WIN 🎉**\n" if res_status == "WIN" else f"❌ **QUOTEX RESULT: LOSS 💔**\n"
            ) + f"📊 Pair: `{pair}`\n🎯 Strategy: `{setup_name}`\n⚡ Signal: `{signal_type}`"
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": result_msg, "parse_mode": "Markdown"}, timeout=5)
            
            with results_lock:
                completed_results.append({"pair": pair, "setup": setup_name, "type": signal_type, "result": res_status})
                if len(completed_results) >= BATCH_SIZE:
                    batch_to_send = completed_results[:BATCH_SIZE]
                    del completed_results[:BATCH_SIZE]
                    send_batch_summary(batch_to_send)
    except Exception as e:
        print(f"Quotex Result Tracking Error: {e}")

def send_batch_summary(results_list):
    win_count = sum(1 for r in results_list if r["result"] == "WIN")
    loss_count = sum(1 for r in results_list if r["result"] == "LOSS")
    win_rate = round((win_count / BATCH_SIZE) * 100, 2)
    
    summary_lines = [
        f"📊 **BATCH SUMMARY (Last {BATCH_SIZE} Signals)** 📊\n",
        f"✅ **Total Wins:** `{win_count}`",
        f"❌ **Total Losses:** `{loss_count}`",
        f"🎯 **Win Rate:** `{win_rate}%`\n",
        f"📌 **Strategy Breakdown:**"
    ]
    
    strategy_stats = {}
    for r in results_list:
        st = r["setup"]
        if st not in strategy_stats:
            strategy_stats[st] = {"win": 0, "loss": 0}
        strategy_stats[st][r["result"].lower()] += 1
        
    for st, stats in strategy_stats.items():
        summary_lines.append(f"• `{st}` ➔ Win: {stats['win']} | Loss: {stats['loss']}")
        
    message = "\n".join(summary_lines)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print(f"Batch Telegram Alert Error: {e}")
        
