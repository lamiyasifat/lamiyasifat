def check_setup_5(df):
    """ Setup 5: Support Doji Reversal with 3 Red Candles Progression (CALL) """
    if len(df) < 10: return None
    
    # Support level calculation (excluding the current doji candle)
    sup = df['low'].iloc[:-1].rolling(window=20, min_periods=5).min().iloc[-1]
    
    # Candles mapping:
    # c4, c3, c2 = ধারাবাহিক ৩টি লাল ক্যান্ডেল (মার্কেট নিচে নামার progression)
    # c1 = ৪নং বা সাম্প্রতিক ক্যান্ডেলটি (ডজি ক্যান্ডেল)
    c4 = df.iloc[-4]
    c3 = df.iloc[-3]
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]  # Doji Candle
    
    # 1. মার্কেট প্রথমার্ধে ধারাবাহিক ৩টি লাল ক্যান্ডেল নিয়ে নিচে নামবে
    is_three_red = (c4['close'] < c4['open']) and \
                   (c3['close'] < c3['open']) and \
                   (c2['close'] < c2['open'])
                   
    # 2. ডজি ক্যান্ডেল শর্ত: বডি টোটাল রেঞ্জের ১২% বা তার কম হতে হবে
    body = abs(c1['close'] - c1['open'])
    total_range = c1['high'] - c1['low']
    is_doji = body <= (total_range * 0.12) if total_range > 0 else False
    
    # 3. সাপোর্ট টাচ এবং ক্লোজিং রুলস
    touches_support = c1['low'] <= sup * 1.005
    closes_above_support = c1['close'] >= sup
    
    # সব শর্ত শতভাগ মিলে গেলে CALL সিগন্যাল রিটার্ন করবে
    if is_three_red and is_doji and touches_support and closes_above_support:
        return "CALL", "Setup-5 (Support Doji Reversal)"
        
    return None, None
    
