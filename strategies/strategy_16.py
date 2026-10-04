def check_setup_16(df):
    """ Setup 16: Strict Reversal Setup with First-Line Serial Green Check (PUT) """
    if len(df) < 15: 
        return None, None
        
    # ১. প্রথমার্ধের প্রথম লাইন চেক: মার্কেট প্রথমে ৩টি সিরিয়াল (consecutive) সবুজ ক্যান্ডেল দিয়ে উপরে উঠেছে কিনা
    # এখানে আমরা বক্সের শুরুর ৩টি ক্যান্ডেল যাচাই করছি
    c_start1 = df.iloc[-9]
    c_start2 = df.iloc[-8]
    c_start3 = df.iloc[-7]
    
    is_initial_serial_green = (c_start1['close'] > c_start1['open']) and \
                               (c_start2['close'] > c_start2['open']) and \
                               (c_start3['close'] > c_start3['open'])
                               
    if not is_initial_serial_green:
        return None, None  # প্রথমার্ধের শর্ত না মিললে সাথে সাথে স্কিপ করবে (ফেক সিগন্যাল জিরো টলারেন্স)
        
    # বক্সের রেজিস্ট্যান্স লেভেল নির্ধারণ (ঐ ৩টি সবুজ ক্যান্ডেলের সর্বোচ্চ হাই)
    resistance_level = max(c_start1['high'], c_start2['high'], c_start3['high'])
    
    # ২. মাঝের অংশ: বক্সের পর মার্কেট নিচের দিকে নামবে (Red candles check)
    intermediate = df.iloc[-6:-2]
    has_down_movement = any(c['close'] < c['open'] for _, c in intermediate.iterrows())
    
    if not has_down_movement:
        return None, None
        
    # ৩. শেষ অংশ: ২নং সবুজ ক্যান্ডেল হয়ে রেজিস্ট্যান্স লেভেল ব্রেক করে উপরে ক্লোজ দেওয়া
    c_break = df.iloc[-1]
    is_break_green = c_break['close'] > c_break['open']
    breaks_resistance = (c_break['close'] > resistance_level) and (c_break['open'] <= resistance_level)
    
    # সব শর্ত শতভাগ মিলে গেলে তবেই PUT সিগন্যাল দেবে
    if is_break_green and breaks_resistance:
        return "PUT", "Setup-16 (Strict Serial Box Reversal PUT)"
        
    return None, None
    
