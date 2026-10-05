import os
import threading
import time
import requests

# Security Config (Environment Variables থেকে মান নিবে)
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", "8987552374:AAHrQelLpyx7CPM-pSBdJRsexiA9pc5vSzw"
)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6885238220")

# ২০টি সিগন্যাল ট্র্যাক করার গ্লোবাল লিস্ট ও লক
completed_results = []
results_lock = threading.Lock()
BATCH_SIZE = 20


def send_telegram_signal(qtx_ws, pair, setup_name, signal_type):
    """১. সিগন্যাল টেলিগ্রামে পাঠাবে এবং রেজাল্ট ট্র্যাকিং শুরু করবে"""
    emoji = "🟢 CALL (BUY)" if signal_type == "CALL" else "🔴 PUT (SELL)"

    message = (
        f"🚨 **QUOTEX OTC SIGNAL (1M)** 🚨\n\n"
        f"📊 **Pair:** `{pair}`\n"
        f"🎯 **Strategy:** `{setup_name}`\n"
        f"⚡ **Direction:** {emoji}\n"
        f"⏱ **Timeframe:** 1 Minute\n\n"
        f"⚠️ *00:00 সেকেন্ডে এন্ট্রি নিন!*"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            t = threading.Thread(
                target=track_quotex_result,
                args=(qtx_ws, pair, setup_name, signal_type),
            )
            t.daemon = True
            t.start()
    except Exception as e:
        print(f"Telegram Alert Error: {e}")


def track_quotex_result(qtx_ws, pair, setup_name, signal_type):
    """১ মিনিট পর রেজাল্ট (WIN অথবা LOSS) চেক করবে"""
    time.sleep(60)

    try:
        df = qtx_ws.get_pair_df(pair)

        if not df.empty and len(df) >= 2:
            last_candle = df.iloc[-2]  # শেষ সমাপ্ত ক্যান্ডেল
            open_price = last_candle["open"]
            close_price = last_candle["close"]

            # ক্যান্ডেল ডিরেকশন নির্ণয়
            if close_price > open_price:
                actual_result = "CALL"
            else:
                actual_result = "PUT"

            # WIN এবং LOSS ফিল্টার
            if actual_result == signal_type:
                res_status = "WIN"
                result_msg = (
                    f"✅ **QUOTEX RESULT: WIN 🎉**\n"
                    f"📊 Pair: `{pair}`\n"
                    f"🎯 Strategy: `{setup_name}`\n"
                    f"⚡ Signal: `{signal_type}`"
                )
            else:
                res_status = "LOSS"
                result_msg = (
                    f"❌ **QUOTEX RESULT: LOSS 💔**\n"
                    f"📊 Pair: `{pair}`\n"
                    f"🎯 Strategy: `{setup_name}`\n"
                    f"⚡ Signal: `{signal_type}`"
                )

            # রেজাল্ট নোটিফিকেশন
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": result_msg,
                    "parse_mode": "Markdown",
                },
                timeout=5,
            )

            # ব্যাচ কাউন্টারে যুক্ত করা
            with results_lock:
                completed_results.append({
                    "pair": pair,
                    "setup": setup_name,
                    "type": signal_type,
                    "result": res_status,
                })

                if len(completed_results) >= BATCH_SIZE:
                    batch_to_send = completed_results[:BATCH_SIZE]
                    del completed_results[:BATCH_SIZE]
                    send_batch_summary(batch_to_send)

    except Exception as e:
        print(f"Quotex Result Tracking Error: {e}")


def send_batch_summary(results_list):
    """২০টি সিগন্যাল শেষে WIN/LOSS সামারি রিপোর্ট পাঠানো"""
    win_count = sum(1 for r in results_list if r["result"] == "WIN")
    loss_count = sum(1 for r in results_list if r["result"] == "LOSS")
    win_rate = round((win_count / BATCH_SIZE) * 100, 2)

    summary_lines = [
        f"📊 **BATCH SUMMARY (Last {BATCH_SIZE} Signals)** 📊\n",
        f"✅ **Total Wins:** `{win_count}`",
        f"❌ **Total Losses:** `{loss_count}`",
        f"🎯 **Win Rate:** `{win_rate}%`\n",
        f"📌 **Strategy Breakdown:**",
    ]

    strategy_stats = {}
    for r in results_list:
        st = r["setup"]
        if st not in strategy_stats:
            strategy_stats[st] = {"win": 0, "loss": 0}
        strategy_stats[st][r["result"].lower()] += 1

    for st, stats in strategy_stats.items():
        summary_lines.append(
            f"• `{st}` ➔ Win: {stats['win']} | Loss: {stats['loss']}"
        )

    message = "\n".join(summary_lines)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
            timeout=5,
        )
    except Exception as e:
        print(f"Batch Telegram Alert Error: {e}")

