def check_setup_6(df):
    """ Setup 6: Resistance Doji Reversal with Uptrend Progression (PUT) """
    if len(df) < 10: return None
    
    # Resistance level calculation (excluding the current doji candle)
    res = df['high'].iloc[:-1].rolling(window=20, min_periods=5).max().iloc[-1]
    
    # Candles mapping:
    # c4, c3, c2 = ধারাবাহিক ৩টি সবুজ ক্যান্ডেল (মার্কেট ওপরে ওঠার progression)
    # c1 = ৪নং বা সাম্প্রতিক ক্যান্ডেলটি (ডজি ক্যান্ডেল)
    c4 = df.iloc[-4]
    c3 = df.iloc[-3]
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]  # Doji Candle
    
    # 1. মার্কেট প্রথমার্ধে ধারাবাহিক ৩টি সবুজ ক্যান্ডেল নিয়ে ওপরে উঠবে
    is_three_green = (c4['close'] > c4['open']) and \
                     (c3['close'] > c3['open']) and \
                     (c2['close'] > c2['open'])
                     
    # 2. ডজি ক্যান্ডেল শর্ত: বডি টোটাল রেঞ্জের ১২% বা তার কম হতে হবে
    body = abs(c1['close'] - c1['open'])
    total_range = c1['high'] - c1['low']
    is_doji = body <= (total_range * 0.12) if total_range > 0 else False
    
    # 3. রেজিস্ট্যান্স টাচ এবং ক্লোজিং রুলস
    touches_resistance = c1['high'] >= res * 0.995
    closes_below_resistance = c1['close'] <= res
    
    # সব শর্ত শতভাগ মিলে গেলে PUT সিগন্যাল রিটার্ন করবে
    if is_three_green and is_doji and touches_resistance and closes_below_resistance:
        return "PUT", "Setup-6 (Resistance Doji Reversal)"
        
    return None, None
    
