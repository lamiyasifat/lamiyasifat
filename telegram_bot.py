import threading
import time
import ccxt
import requests

# Apnar telegram bot token ebong chat ID
TELEGRAM_BOT_TOKEN = "8987552374:AAHrQelLpyx7CPM-pSBdJRsexiA9pc5vSzw"
TELEGRAM_CHAT_ID = "6885238220"

# Binance Futures exchange connection (data check korar jonno)
exchange = ccxt.binance({
    'options': {'defaultType': 'future'},
    'enableRateLimit': True,
})


def get_binance_candles_for_result(symbol):
  """Binance Futures theke signal er result check korar jonno 1 minute candle data ana"""
  try:
    # 1 minute candle onujayi futures data fetch kora
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=5)
    if ohlcv and len(ohlcv) >= 2:
      # Sesh close howa candle ti newar jonno
      last_candle = ohlcv[-2]
      # format: [timestamp, open, high, low, close, volume]
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
      # Win naki loss nirdharon logic (up/down onujayi)
      if close_price > open_price:
        actual_result = 'CALL'  # Sobuj candle (UP)
      elif close_price < open_price:
        actual_result = 'PUT'  # Lal candle (DOWN)
      else:
        actual_result = 'DOJI'

      if actual_result == signal_type:
        result_msg = (
            f'✅ **BINANCE RESULT: WIN 🎉**\n📊 Pair: `{symbol}`\n🎯 Strategy:'
            f' `{setup_name}`\n⚡ Signal was: `{signal_type}`'
        )
      elif actual_result == 'DOJI':
        result_msg = (
            f'⚪ **BINANCE RESULT: DOJI (Tie) ⚠️**\n📊 Pair: `{symbol}`\n🎯'
            f' Strategy: `{setup_name}`'
        )
      else:
        result_msg = (
            f'❌ **BINANCE RESULT: LOSS 💔**\n📊 Pair: `{symbol}`\n🎯 Strategy:'
            f' `{setup_name}`\n⚡ Signal was: `{signal_type}`'
        )

      # Telegram a result pathano
      url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
      payload = {
          'chat_id': TELEGRAM_CHAT_ID,
          'text': result_msg,
          'parse_mode': 'Markdown',
      }
      requests.post(url, json=payload)

  except Exception as e:
    print(f"Result Tracking Error: {e}")


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
      # Background a result track korar jonno thread cholu kora (ekhon setup_name o pass kora hoyeche)
      t = threading.Thread(
          target=track_signal_result, args=(symbol, setup_name, signal_type)
      )
      t.daemon = True
      t.start()

  except Exception as e:
    print(f'Telegram Alert Error: {e}')
      
