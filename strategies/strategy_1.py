def check_setup_1(df):
    """ Setup 1: Resistance Breakout (CALL) - Proper Uptrend Progression & Strict Match """
    if len(df) < 15: return None
    
    # Resistance Level Calculation
    res = df['high'].iloc[:-2].rolling(window=20, min_periods=5).max().iloc[-1]
    
    # Candles mapping for progression check:
    c5 = df.iloc[-6]
    c4 = df.iloc[-5]
    c3 = df.iloc[-4]
    c2_prev = df.iloc[-3]
    c1 = df.iloc[-2]  # 1no Red Candle (Resistance Touch)
    c2 = df.iloc[-1]  # 2no Green Candle (Resistance Breakout)
    
    # 1. Market gochiye oporer dike othar (Uptrend Progression) logic:
    # Aager candle-gulo green hote hobe ebong low/close gulo krome oporer dike jete hobe (dhapiye otha)
    is_green_sequence = (c5['close'] > c5['open']) and \
                        (c4['close'] > c4['open']) and \
                        (c3['close'] > c3['open']) and \
                        (c2_prev['close'] > c2_prev['open'])
                        
    # Progression check: Price consistently higher hochhe kina
    is_price_progressing = (c2_prev['close'] > c3['close']) and (c3['close'] > c4['close'])
    
    is_market_climbing = is_green_sequence and is_price_progressing
    
    # 2. 1no Red candle rules: High touches resistance, close below resistance
    is_c1_red = c1['close'] < c1['open']
    c1_touches_res = (c1['high'] >= res * 0.995) and (c1['close'] < res)
    
    # 3. 2no Green candle rules: Open near/below resistance, close above resistance (Breakout)
    is_c2_green = c2['close'] > c2['open']
    c2_breaks_res = (c2['close'] > res) and (c2['open'] <= res)
    
    # Shob condition 100% match korlei shudhu CALL signal dispatch hobe
    if is_market_climbing and is_c1_red and c1_touches_res and is_c2_green and c2_breaks_res:
        return "CALL"
        
    return None
    
