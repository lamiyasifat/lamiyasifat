def check_setup_19(df):
    """ Setup-19: Continuation Setup Inside Body (CALL) """
    if len(df) < 5: 
        return None, None
        
    c2 = df.iloc[-2]  # ১নং লাল ক্যান্ডেল
    c1 = df.iloc[-1]  # ২নং সবুজ ক্যান্ডেল
    
    # শর্ত ১: c2 লাল ক্যান্ডেল এবং c1 সবুজ ক্যান্ডেল হতে হবে
    is_c2_red = c2['close'] < c2['open']
    is_c1_green = c1['close'] > c1['open']
    
    if not (is_c2_red and is_c1_green):
        return None, None
        
    # শর্ত ২: সবুজ ক্যান্ডেলটি লাল ক্যান্ডেলের বডির ভেতরে ক্লোজ দেবে এবং হাই ব্রেক করবে না
    closes_inside = (c1['close'] <= c2['open']) and (c1['close'] >= c2['close'])
    does_not_break_high = c1['high'] <= c2['high']
    
    if closes_inside and does_not_break_high:
        return "CALL", "Setup-19 (Strict Continuation CALL)"
        
    return None, None
    
