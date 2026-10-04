import threading
import time
import ccxt
import requests

# Apnar telegram bot token ebong chat ID
TELEGRAM_BOT_TOKEN = "8987552374:AAHrQelLpyx7CPM-pSBdJRsexiA9pc5vSzw"
TELEGRAM_CHAT_ID = "6885238220"

# Binance Futures exchange connection
exchange = ccxt.binance({
    'options': {'defaultType': 'future'},
    'enableRateLimit': True,
})

# 20 ta signal track korar jonno global list ebong lock
completed_results = []
results_lock = threading.Lock()
BATCH_SIZE = 20  # Ekhane 20 set kora ache


def get_binance_candles_for_result(symbol):
  """Binance Futures theke 1 minute candle data ana"""
  try:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=5)
    if ohlcv and len(ohlcv) >= 2:
      last_candle = ohlcv[-2]
      return last_candle[1], last_candle[4]  # Open price, Close price
  except Exception as e:
    print(f"Binance Result Fetch Error: {e}")
  return None, None


def track_signal_result(symbol, setup_name, signal_type):
  # 1 minute candle er jonno 60 second opekha kora
  time.sleep(60)

  try:
    open_price, close_price = get_binance_candles_for_result(symbol)

    if open_price is not None and close_price is not None:
      if close_price > open_price:
        actual_result = 'CALL'
      elif close_price < open_price:
        actual_result = 'PUT'
      else:
        actual_result = 'DOJI'

      if actual_result == signal_type:
        res_status = 'WIN'
        result_msg = (
            f'✅ **BINANCE RESULT: WIN 🎉**\n📊 Pair: `{symbol}`\n🎯 Strategy:'
            f' `{setup_name}`\n⚡ Signal was: `{signal_type}`'
        )
      elif actual_result == 'DOJI':
        res_status = 'DOJI'
        result_msg = (
            f'⚪ **BINANCE RESULT: DOJI (Tie) ⚠️**\n📊 Pair: `{symbol}`\n🎯'
            f' Strategy: `{setup_name}`'
        )
      else:
        res_status = 'LOSS'
        result_msg = (
            f'❌ **BINANCE RESULT: LOSS 💔**\n📊 Pair: `{symbol}`\n🎯 Strategy:'
            f' `{setup_name}`\n⚡ Signal was: `{signal_type}`'
        )

      # 1. Proti barer moto individual result telegram a pathano
      url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
      payload = {
          'chat_id': TELEGRAM_CHAT_ID,
          'text': result_msg,
          'parse_mode': 'Markdown',
      }
      requests.post(url, json=payload)

      # 2. 20 ta signal er batch summary er jonno list a add kora
      with results_lock:
        completed_results.append({
            'symbol': symbol,
            'setup': setup_name,
            'type': signal_type,
            'result': res_status,
        })

        if len(completed_results) >= BATCH_SIZE:
          batch_to_send = completed_results[:BATCH_SIZE]
          del completed_results[:BATCH_SIZE]
          send_batch_summary(batch_to_send)

  except Exception as e:
    print(f"Result Tracking Error: {e}")


def send_batch_summary(results_list):
  """20 ta trade purno hole setar upor ভিত্তি kore summary report pathano"""
  win_count = sum(1 for r in results_list if r['result'] == 'WIN')
  loss_count = sum(1 for r in results_list if r['result'] == 'LOSS')
  doji_count = sum(1 for r in results_list if r['result'] == 'DOJI')

  summary_lines = []
  summary_lines.append(
      f'📊 **BATCH SUMMARY (Last {BATCH_SIZE} Signals)** 📊\n'
  )
  summary_lines.append(f'✅ **Total Wins:** `{win_count}`')
  summary_lines.append(f'❌ **Total Losses:** `{loss_count}`')
  summary_lines.append(f'⚪ **Total Doji:** `{doji_count}`\n')
  summary_lines.append(f'📌 **Strategy-wise Breakdown:**')

  strategy_stats = {}
  for r in results_list:
    st = r['setup']
    if st not in strategy_stats:
      strategy_stats[st] = {'win': 0, 'loss': 0, 'doji': 0}
    strategy_stats[st][r['result'].lower()] += 1

  for st, stats in strategy_stats.items():
    summary_lines.append(
        f'• `{st}` ➔ Win: {stats["win"]} | Loss: {stats["loss"]} | Doji:'
        f' {stats["doji"]}'
    )

  message = '\n'.join(summary_lines)

  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {
      'chat_id': TELEGRAM_CHAT_ID,
      'text': message,
      'parse_mode': 'Markdown',
  }
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f'Batch Telegram Alert Error: {e}')


def send_telegram_signal(symbol, setup_name, signal_type):
  """Bot jokhoni signal pabe, ta telegram a pathabe ebong result track korbe"""
  emoji = '🟢 LONG (CALL)' if signal_type == 'CALL' else '🔴 SHORT (PUT)'

  message = (
      f'🚨 **BINANCE FUTURES SIGNAL (1m)** 🚨\n\n'
      f'📊 **Pair:** `{symbol}`\n'
      f'🎯 **Strategy:** `{setup_name}`\n'
      f'⚡ **Direction:** {emoji}\n'
      f'⏱ **Timeframe:** 1 Minute\n\n'
      f'⚠️ *Binance Futures a automatic execute hocche!*'
  )

  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {
      'chat_id': TELEGRAM_CHAT_ID,
      'text': message,
      'parse_mode': 'Markdown',
  }

  try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
      t = threading.Thread(
          target=track_signal_result, args=(symbol, setup_name, signal_type)
      )
      t.daemon = True
      t.start()

  except Exception as e:
    print(f'Telegram Alert Error: {e}')
      
