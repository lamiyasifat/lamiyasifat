def check_setup_7(df):
    """ Setup 7: Strict Resistance Pullback Reversal with Exact Match Check (CALL) """
    if len(df) < 15: 
        return None, None
        
    # Dynamic Resistance Calculation (excluding recent candles)
    res = df['high'].iloc[:-3].rolling(window=20, min_periods=5).max().iloc[-1]
    
    # 1. Prothom dike market upore uthbe (3 ti consecutive green candles er proper check)
    c6 = df.iloc[-6]
    c5 = df.iloc[-5]
    c4 = df.iloc[-4]
    
    is_initial_uptrend = (c6['close'] > c6['open']) and \
                         (c5['close'] > c5['open']) and \
                         (c4['close'] > c4['open'])
                         
    if not is_initial_uptrend:
        return None, None  # Condition match na korle immediate skip korbe
                         
    # 2. Setup-er sesh 3 ti candle mapping:
    s7_1 = df.iloc[-3]  # ১নং সবুজ ক্যান্ডেল (breakout)
    s7_2 = df.iloc[-2]  # ২নং সবুজ ক্যান্ডেল
    s7_3 = df.iloc[-1]  # ৩নং লাল ক্যান্ডেল (pullback)
    
    is_s7_c1_green = s7_1['close'] > s7_1['open']
    s7_c1_breaks = (s7_1['close'] > res) and (s7_1['open'] <= res)
    is_s7_c2_green = s7_2['close'] > s7_2['open']
    is_s7_c3_red = s7_3['close'] < s7_3['open']
    
    # 3. SNR Touch & Closing Check (Strict Rule)
    s7_touches_res = s7_3['low'] <= res * 1.005
    s7_closes_above_res = s7_3['close'] >= res
    
    # Shobguli sharto 100% mile gelei shudu signal dibe, nahole None ferot dibe jate bot onno guli scan korte pare
    if is_s7_c1_green and s7_c1_breaks and is_s7_c2_green and is_s7_c3_red and s7_touches_res and s7_closes_above_res:
        return "CALL", "Setup-7 (Strict Resistance Pullback Reversal)"
        
    return None, None
    
