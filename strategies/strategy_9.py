def check_setup_9(df):
    """ Setup 9: Reversal Setup (CALL) """
    if len(df) < 10: 
        return None, None
        
    # ক্যান্ডেল ম্যাপিং:
    # c4 = ছোট লাল ক্যান্ডেল (শুরুর ক্যান্ডেল)
    # c3 = ১নং সবুজ ক্যান্ডেল (প্রথম সবুজ)
    # c2 = ১নং-এর মতো ২য় সবুজ ক্যান্ডেল (দ্বিতীয় সবুজ)
    # c1 = ২নং বড় লাল ক্যান্ডেল (যা আগের সবুজগুলোকে কভার করে নিচে ক্লোজ দেবে)
    c4 = df.iloc[-4]
    c3 = df.iloc[-3]
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]
    
    # শর্ত ১: শুরুতে একটি লাল ক্যান্ডেল এবং তার পরে পরপর ২টি সবুজ ক্যান্ডেল থাকবে
    is_c4_red = c4['close'] < c4['open']
    is_c3_green = c3['close'] > c3['open']
    is_c2_green = c2['close'] > c2['open']
    
    # শর্ত ২: ২নং ক্যান্ডেলটি (c1) একটি বড় লাল ক্যান্ডেল হবে
    is_c1_red = c1['close'] < c1['open']
    
    # শর্ত ৩: লাল ক্যান্ডেলটি (c1) সবুজ ক্যান্ডেল দুটির নিচে ক্লোজ দেবে (অর্থাৎ c1-এর low বা close আগের সবুজগুলোর নিচে থাকবে)
    closes_below_greens = (c1['close'] < c3['low']) and (c1['open'] >= c2['close'])
    
    # সব শর্ত ১০০% মিলে গেলে সিগন্যাল দেবে, না হলে স্কিপ করবে
    if is_c4_red and is_c3_green and is_c2_green and is_c1_red and closes_below_greens:
        return "CALL", "Setup-9 (Reversal Setup)"
        
    return None, None
    
