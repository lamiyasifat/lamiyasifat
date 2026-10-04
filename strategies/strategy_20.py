def check_setup_20(df):
    """ Setup-20: Continuation Setup Inside Body (PUT) """
    if len(df) < 5: 
        return None, None
        
    c2 = df.iloc[-2]  # ১নং সবুজ ক্যান্ডেল
    c1 = df.iloc[-1]  # ২নং লাল ক্যান্ডেল
    
    # শর্ত ১: c2 সবুজ ক্যান্ডেল এবং c1 লাল ক্যান্ডেল হতে হবে
    is_c2_green = c2['close'] > c2['open']
    is_c1_red = c1['close'] < c1['open']
    
    if not (is_c2_green and is_c1_red):
        return None, None
        
    # শর্ত ২: লাল ক্যান্ডেলটি সবুজ ক্যান্ডেলের বডির ভেতরে ক্লোজ দেবে এবং লো ব্রেক করবে না
    closes_inside = (c1['close'] >= c2['open']) and (c1['close'] <= c2['close'])
    does_not_break_low = c1['low'] >= c2['low']
    
    if closes_inside and does_not_break_low:
        return "PUT", "Setup-20 (Strict Continuation PUT)"
        
    return None, None
    
