def check_setup_2(df):
    """ Setup 2: Support Breakout (PUT) - Proper Downtrend Progression & Strict Match """
    if len(df) < 15: return None
    
    # Support Level Calculation (Rolling Low)
    sup = df['low'].iloc[:-2].rolling(window=20, min_periods=5).min().iloc[-1]
    
    # Candles mapping for progression check (Downtrend):
    c5 = df.iloc[-6]
    c4 = df.iloc[-5]
    c3 = df.iloc[-4]
    c2_prev = df.iloc[-3]
    c1 = df.iloc[-2]  # 1no Green Candle (Support Touch)
    c2 = df.iloc[-1]  # 2no Red Candle (Support Breakout)
    
    # 1. Market gochiye nicher dike namar (Downtrend Progression) logic:
    # Aager candle-gulo red hote hobe ebong high/close gulo krome nicher dike namte hobe
    is_red_sequence = (c5['close'] < c5['open']) and \
                      (c4['close'] < c4['open']) and \
                      (c3['close'] < c3['open']) and \
                      (c2_prev['close'] < c2_prev['open'])
                      
    # Progression check: Price consistently lower jacche kina
    is_price_dropping = (c2_prev['close'] < c3['close']) and (c3['close'] < c4['close'])
    
    is_market_falling = is_red_sequence and is_price_dropping
    
    # 2. 1no Green candle rules: Low touches support, close above support
    is_c1_green = c1['close'] > c1['open']
    c1_touches_sup = (c1['low'] <= sup * 1.005) and (c1['close'] > sup)
    
    # 3. 2no Red candle rules: Open near/above support, close below support (Breakout)
    is_c2_red = c2['close'] < c2['open']
    c2_breaks_sup = (c2['close'] < sup) and (c2['open'] >= sup)
    
    # Shob condition 100% match korlei shudhu PUT signal dispatch hobe
    if is_market_falling and is_c1_green and c1_touches_sup and is_c2_red and c2_breaks_sup:
        return "PUT"
        
    return None
    
