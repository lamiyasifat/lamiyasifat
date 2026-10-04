def check_setup_4(df):
    """ Setup 4: Four Green Candles with Size Match (PUT) - Strict & Mojbot """
    if len(df) < 10: return None
    
    # শেষ ৪টি ক্যান্ডেল ম্যাপিং:
    # c4 = ১নং সবুজ ক্যান্ডেল (সবচেয়ে পেছনেরটি)
    # c3 = ২নং সবুজ ক্যান্ডেল
    # c2 = ৩নং সবুজ ক্যান্ডেল
    # c1 = ৪নং বড় সবুজ ক্যান্ডেল (সাম্প্রতিকটি)
    c4 = df.iloc[-4]
    c3 = df.iloc[-3]
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]
    
    # ১. কন্ডিশন: চারটি ক্যান্ডেলই সবুজ (Green) হতে হবে
    is_all_green = (c4['close'] > c4['open']) and \
                   (c3['close'] > c3['open']) and \
                   (c2['close'] > c2['open']) and \
                   (c1['close'] > c1['open'])
                 
    if not is_all_green:
        return None
        
    # ২. ক্যান্ডেলগুলোর সাইজ (High - Low) হিসাব:
    size_4 = abs(c4['high'] - c4['low'])  # ১নং ক্যান্ডেল
    size_3 = abs(c3['high'] - c3['low'])  # ২নং ক্যান্ডেল
    size_2 = abs(c2['high'] - c2['low'])  # ৩নং ক্যান্ডেল
    size_1 = abs(c1['high'] - c1['low'])  # ৪নং ক্যান্ডেল (বড় ক্যান্ডেলটি)
    
    # প্রথম ৩টি ক্যান্ডেলের টোটাল সাইজ
    total_prev_size = size_4 + size_3 + size_2
    
    # ৩. সাইজ ম্যাচিং কন্ডিশন (২০% টলারেন্স রাখা হলো যাতে সামান্য তারতম্যেও মিস না করে)
    tolerance = 0.20
    is_size_matched = (total_prev_size >= size_1 * (1 - tolerance)) and \
                      (total_prev_size <= size_1 * (1 + tolerance))
                      
    # সব শর্ত শতভাগ মিলে গেলে PUT সিগন্যাল রিটার্ন করবে
    if is_all_green and is_size_matched:
        return "PUT"
        
    return None
    
