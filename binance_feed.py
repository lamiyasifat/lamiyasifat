import ccxt
import pandas as pd

# আপনার বাইন্যান্সের অরিজিনাল এপিআই কি এবং সিক্রেট কোড
BINANCE_API_KEY = "mncoq6u6QxoNQiw0IKMxBi1IpRCqtffmcCg7r45757KJkrsPNoWI68qAMMXmzipt"
BINANCE_SECRET_KEY = "165K38LnOfS7mjcPd3Bt5GuOaEVXY1CgcdTv0sDTg5Mf1REbvnIZvo4dVYBfJPQN"

# বাইন্যান্স ফিউচার্স এক্সচেঞ্জ কানেকশন ইনিশিয়ালাইজ করা
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'options': {'defaultType': 'future'},  # ফিউচার্স ট্রেডিং মোড
    'enableRateLimit': True,  # রেট লিমিট প্রটেকশন
})


def get_binance_futures_candles(symbol, timeframe='1m', limit=100):
    """বাইন্যান্স ফিউচার্স থেকে লাইভ ক্যান্ডেল ডেটা ফেচ করার ফাংশন (ডিফল্ট ১ মিনিট)"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if ohlcv:
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'],
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except Exception as e:
        print(f"Binance API Error for {symbol}: {e}")
    return None
    
