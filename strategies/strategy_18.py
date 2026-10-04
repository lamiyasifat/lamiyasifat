def check_setup_18(df):
    """ Setup-18: Decreasing Green Candles Followed by Bearish Engulfing (PUT) """
    if len(df) < 10: 
        return None, None
        
    c4 = df.iloc[-4]  # ১ম সবুজ ক্যান্ডেল (বড়)
    c3 = df.iloc[-3]  # ২য় সবুজ ক্যান্ডেল (মাঝারি)
    c2 = df.iloc[-2]  # ৩য় সবুজ ক্যান্ডেল (ছোট)
    c1 = df.iloc[-1]  # ৪র্থ লাল ক্যান্ডেল (Engulfing)
    
    # শর্ত ১: প্রথম ৩টি ক্যান্ডেল সবুজ হতে হবে
    is_c4_green = c4['close'] > c4['open']
    is_c3_green = c3['close'] > c3['open']
    is_c2_green = c2['close'] > c2['open']
    
    if not (is_c4_green and is_c3_green and is_c2_green):
        return None, None
        
    # শর্ত ২: ক্যান্ডেলগুলোর বডি সাইজ ক্রমান্বয়ে ছোট হতে হবে
    body_4 = abs(c4['close'] - c4['open'])
    body_3 = abs(c3['close'] - c3['open'])
    body_2 = abs(c2['close'] - c2['open'])
    
    is_decreasing = (body_4 > body_3) and (body_3 > body_2)
    if not is_decreasing:
        return None, None
        
    # শর্ত ৩: শেষ ক্যান্ডেলটি (c1) লাল হবে এবং ৩য় সবুজ ক্যান্ডেলকে (c2) এনগালফ করবে
    is_c1_red = c1['close'] < c1['open']
    engulfs = (c1['close'] <= c2['open']) and (c1['open'] >= c2['close'])
    
    if is_c1_red and engulfs:
        return "PUT", "Setup-18 (Strict Decreasing Green Engulfing PUT)"
        
    return None, None
    
