def check_setup_8(df):
    """ Setup 8: Strict Support Pullback Reversal (PUT) """
    if len(df) < 15: 
        return None, None
        
    # Dynamic Support Calculation (excluding recent candles)
    sup = df['low'].iloc[:-3].rolling(window=20, min_periods=5).min().iloc[-1]
    
    # 1. Prothom dike market nicher dike jabe (3 ti consecutive red candles er proper check)[span_2](start_span)[span_2](end_span)
    c6 = df.iloc[-6]
    c5 = df.iloc[-5]
    c4 = df.iloc[-4]
    
    is_initial_downtrend = (c6['close'] < c6['open']) and \
                           (c5['close'] < c5['open']) and \
                           (c4['close'] < c4['open'])
                         
    if not is_initial_downtrend:
        return None, None  # Condition match na korle immediate skip korbe
                         
    # 2. Setup-er sesh 3 ti candle mapping:
    s8_1 = df.iloc[-3]  # ১নং লাল ক্যান্ডেল (breakout)[span_3](start_span)[span_3](end_span)
    s8_2 = df.iloc[-2]  # ২নং লাল ক্যান্ডেল[span_4](start_span)[span_4](end_span)
    s8_3 = df.iloc[-1]  # ৩নং সবুজ ক্যান্ডেল (pullback)[span_5](start_span)[span_5](end_span)
    
    is_s8_c1_red = s8_1['close'] < s8_1['open']
    s8_c1_breaks = (s8_1['close'] < sup) and (s8_1['open'] >= sup)[span_6](start_span)[span_6](end_span)
    is_s8_c2_red = s8_2['close'] < s8_2['open'][span_7](start_span)[span_7](end_span)
    is_s8_c3_green = s8_3['close'] > s8_3['open'][span_8](start_span)[span_8](end_span)
    
    # 3. SNR Touch & Closing Check (Strict Rule: touches support and closes below support)[span_9](start_span)[span_9](end_span)
    s8_touches_sup = s8_3['high'] >= sup * 0.995
    s8_closes_below_sup = s8_3['close'] <= sup
    
    if is_s8_c1_red and s8_c1_breaks and is_s8_c2_red and is_s8_c3_green and s8_touches_sup and s8_closes_below_sup:
        return "PUT", "Setup-8 (Strict Support Pullback Reversal)"
        
    return None, None
    
