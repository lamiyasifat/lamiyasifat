def check_setup_10(df):
    """ Setup 10: Reversal Setup with Initial Green Candle Check (PUT / Down)[span_2](start_span)[span_2](end_span) """
    if len(df) < 10: 
        return None, None
        
    # ক্যান্ডেল ম্যাপিং:
    # c4 = শুরুতে ছোট সবুজ ক্যান্ডেল (বাম পাশের ক্যান্ডেল)[span_3](start_span)[span_3](end_span)
    # c3 = ১নং লাল ক্যান্ডেল (প্রথম লাল)[span_4](start_span)[span_4](end_span)
    # c2 = ১নং-এর মতো ২য় লাল ক্যান্ডেল (দ্বিতীয় লাল)[span_5](start_span)[span_5](end_span)
    # c1 = ২নং বড় সবুজ ক্যান্ডেল (যা লাল ক্যান্ডেল দুটির ওপরে ক্লোজ দেবে)[span_6](start_span)[span_6](end_span)
    c4 = df.iloc[-4]
    c3 = df.iloc[-3]
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]
    
    # শর্ত ১: শুরুতে একটি ছোট সবুজ ক্যান্ডেল এবং তার পরে পরপর ২টি লাল ক্যান্ডেল থাকবে[span_7](start_span)[span_7](end_span)
    is_c4_green = c4['close'] > c4['open']
    is_c3_red = c3['close'] < c3['open']
    is_c2_red = c2['close'] < c2['open']
    
    # শর্ত ২: শেষ ক্যান্ডেলটি (c1) সবুজ ক্যান্ডেল হবে[span_8](start_span)[span_8](end_span)
    is_c1_green = c1['close'] > c1['open']
    
    # শর্ত ৩: সবুজ ক্যান্ডেলটি লাল ক্যান্ডেল দুটির ওপরে ক্লোজ দেবে[span_9](start_span)[span_9](end_span)
    closes_above_reds = (c1['close'] > c3['high']) and (c1['open'] <= c2['close'])
    
    # সব শর্ত ১০০% মিলে গেলে PUT সিগন্যাল দেবে, না হলে স্কিপ করবে[span_10](start_span)[span_10](end_span)
    if is_c4_green and is_c3_red and is_c2_red and is_c1_green and closes_above_reds:
        return "PUT", "Setup-10 (Strict Reversal Setup Down)[span_11](start_span)"[span_11](end_span)
        
    return None, None
    
