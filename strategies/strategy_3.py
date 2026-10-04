def check_setup_3(df):
    """ Setup 3: Four Red Candles with Size Match (CALL) - Strict & Mojbot """
    if len(df) < 10: return None
    
    # শেষ ৪টি ক্যান্ডেল ম্যাপিং:
    # c4 = ১নং লাল ক্যান্ডেল (সবচেয়ে পেছনেরটি)
    # c3 = ২নং লাল ক্যান্ডেল
    # c2 = ৩নং লাল ক্যান্ডেল
    # c1 = ৪নং বড় লাল ক্যান্ডেল (সাম্প্রতিকটি)
    c4 = df.iloc[-4]
    c3 = df.iloc[-3]
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]
    
    # ১. কন্ডিশন: চারটি ক্যান্ডেলই লাল (Red) হতে হবে
    is_all_red = (c4['close'] < c4['open']) and \
                 (c3['close'] < c3['open']) and \
                 (c2['close'] < c2['open']) and \
                 (c1['close'] < c1['open'])
                 
    if not is_all_red:
        return None
        
    # ২. ক্যান্ডেলগুলোর সাইজ (High - Low) হিসাব:
    size_4 = abs(c4['high'] - c4['low'])  # ১নং ক্যান্ডেল
    size_3 = abs(c3['high'] - c3['low'])  # ২নং ক্যান্ডেল
    size_2 = abs(c2['high'] - c2['low'])  # ৩নং ক্যান্ডেল
    size_1 = abs(c1['high'] - c1['low'])  # ৪নং ক্যান্ডেল (বড় ক্যান্ডেলটি)
    
    # প্রথম ৩টি ক্যান্ডেলের টোটাল সাইজ
    total_prev_size = size_4 + size_3 + size_2
    
    # ৩. সাইজ ম্যাচিং কন্ডিশন (১+২+৩ এর সাইজ ৪নং এর সমান বা কাছাকাছি হতে হবে, যেমন ১০-১৫% টলারেন্স রাখা নিরাপদ)
    # যাতে সামান্য কম-বেশি হলেও বট মিস না করে, আবার হুবহু নিখুঁত থাকে
    tolerance = 0.20  # ২০% এলাউন্স রাখা হলো ফ্লেক্সিবিইটির জন্য
    is_size_matched = (total_prev_size >= size_1 * (1 - tolerance)) and \
                      (total_prev_size <= size_1 * (1 + tolerance))
                      
    # সব শর্ত শতভাগ মিলে গেলে CALL সিগন্যাল রিটার্ন করবে
    if is_all_red and is_size_matched:
        return "CALL"
        
    return None
    
