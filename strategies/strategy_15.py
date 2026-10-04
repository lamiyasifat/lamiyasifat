def check_setup_15(df):
    """ Setup 15: Reversal Setup with Strict Support Box & Pullback Check (CALL)[span_2](start_span)[span_2](end_span) """
    if len(df) < 15: 
        return None, None
        
    # ১. প্রথমে সাপোর্ট লেভেল বা বক্সের লোয়ার লিমিট বের করা (১নং বক্সের লো পয়েন্ট)
    # এখানে আমরা শেষ দিকের ক্যান্ডেলগুলোর আগের ডাটা থেকে সাপোর্ট লেভেল নির্ধারণ করছি
    support_level = df['low'].iloc[-10:-4].min()
    
    # ক্যান্ডেল ম্যাপিং (শেষের দিক থেকে):
    # s15_1 = ২নং লাল ক্যান্ডেল (যা সাপোর্ট ব্রেক করে নিচে ক্লোজ দেবে)[span_3](start_span)[span_3](end_span)
    # মাঝখানে কিছু সবুজ ক্যান্ডেল থাকবে যা ওপরের দিকে গিয়েছিল[span_4](start_span)[span_4](end_span)
    # বামের বক্সে সর্বনিম্ন ২ বা সর্বোচ্চ ৩টি লাল ক্যান্ডেল থাকবে[span_5](start_span)[span_5](end_span)
    
    c1 = df.iloc[-1]  # বর্তমান শেষ ক্যান্ডেল (২নং লাল ক্যান্ডেল যা ব্রেক করবে)[span_6](start_span)[span_6](end_span)
    
    # শর্ত ১: শেষ ক্যান্ডেলটি অবশ্যই লাল হতে হবে এবং সাপোর্ট লেভেল ব্রেক করে নিচে ক্লোজ দিতে হবে[span_7](start_span)[span_7](end_span)
    is_c1_red = c1['close'] < c1['open']
    breaks_support = (c1['close'] < support_level) and (c1['open'] >= support_level)
    
    if not (is_c1_red and breaks_support):
        return None, None  # শর্ত না মিললে সাথে সাথে স্কিপ করবে (ফেক সিগন্যাল বাদ)
        
    # শর্ত ২: বামের বক্সে সর্বনিম্ন ২ থেকে সর্বোচ্চ ৩টি লাল ক্যান্ডেল ছিল কিনা এবং একটি সাপোর্ট জোন তৈরি করেছিল কিনা তা যাচাই
    # আমরা ধরে নিচ্ছি c1 এর অন্তত ৪-৫ ক্যান্ডেল আগে একটি ডাউন মুভমেন্ট এবং বক্সের লো পয়েন্ট ছিল
    box_candles = df.iloc[-8:-4] # বক্সের ভেতরের ক্যান্ডেলগুলো
    red_count_in_box = sum(1 for i in range(len(box_candles)) if box_candles.iloc[i]['close'] < box_candles.iloc[i]['open'])
    
    # সর্বনিম্ন ২ বা সর্বোচ্চ ৩টি লাল ক্যান্ডেল থাকতে হবে[span_8](start_span)[span_8](end_span)
    has_valid_red_box = 2 <= red_count_in_box <= 3
    
    # শর্ত ৩: মাঝের অংশে মার্কেট ওপরের দিকে গিয়েছিল (Green candles progression)[span_9](start_span)[span_9](end_span)
    intermediate_candles = df.iloc[-4:-1]
    has_up_movement = any(c['close'] > c['open'] for _, c in intermediate_candles.iterrows())
    
    # সব শর্ত ১০০% কঠোরভাবে মিলে গেলে তবেই CALL সিগন্যাল দেবে, অন্যথায় স্কিপ করবে[span_10](start_span)[span_10](end_span)
    if has_valid_red_box and has_up_movement:
        return "CALL", "Setup-15 (Strict Reversal Setup CALL)[span_11](start_span)"[span_11](end_span)
        
    return None, None
    
