def check_setup_17(df):
    """ Setup-17: Decreasing Red Candles Followed by Bullish Engulfing (CALL) """
    if len(df) < 10: 
        return None, None
        
    c4 = df.iloc[-4]  # ১ম লাল ক্যান্ডেল (বড়)
    c3 = df.iloc[-3]  # ২য় লাল ক্যান্ডেল (মাঝারি)
    c2 = df.iloc[-2]  # ৩য় লাল ক্যান্ডেল (ছোট)
    c1 = df.iloc[-1]  # ৪র্থ সবুজ ক্যান্ডেল (Engulfing)
    
    # শর্ত ১: প্রথম ৩টি ক্যান্ডেল লাল হতে হবে
    is_c4_red = c4['close'] < c4['open']
    is_c3_red = c3['close'] < c3['open']
    is_c2_red = c2['close'] < c2['open']
    
    if not (is_c4_red and is_c3_red and is_c2_red):
        return None, None
        
    # শর্ত ২: ক্যান্ডেলগুলোর বডি সাইজ আস্তে আস্তে ছোট হতে হবে (100% > 60% > 40% নিয়ম)
    body_4 = abs(c4['close'] - c4['open'])
    body_3 = abs(c3['close'] - c3['open'])
    body_2 = abs(c2['close'] - c2['open'])
    
    is_decreasing = (body_4 > body_3) and (body_3 > body_2)
    if not is_decreasing:
        return None, None
        
    # শর্ত ৩: শেষ ক্যান্ডেলটি (c1) সবুজ হবে এবং ৩য় লাল ক্যান্ডেলকে (c2) পুরোপুরি এনগালফ করবে
    is_c1_green = c1['close'] > c1['open']
    engulfs = (c1['close'] >= c2['open']) and (c1['open'] <= c2['close'])
    
    if is_c1_green and engulfs:
        return "CALL", "Setup-17 (Strict Decreasing Red Engulfing CALL)"
        
    return None, None
    
