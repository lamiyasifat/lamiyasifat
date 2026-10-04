def check_setup_1(df):
    """ Setup 1: Resistance Breakout (CALL) - Strict & Mojbot """
    if len(df) < 10: return None
    
    # Resistance Level Calculation (Recent highs excluding current 2 candles)
    res = df['high'].iloc[:-2].rolling(window=20, min_periods=5).max().iloc[-1]
    
    c1 = df.iloc[-2]  # 1no Red Candle
    c2 = df.iloc[-1]  # 2no Green Breakout Candle
    
    # 1no Red candle strict rules: Must be red, high touches resistance zone, close below resistance
    is_c1_red = c1['close'] < c1['open']
    c1_touches_res = (c1['high'] >= res * 0.995) and (c1['close'] < res)
    
    # 2no Green candle strict rules: Must be green, opens near/below resistance and closes above resistance
    is_c2_green = c2['close'] > c2['open']
    c2_breaks_res = (c2['close'] > res) and (c2['open'] <= res)
    
    if is_c1_red and c1_touches_res and is_c2_green and c2_breaks_res:
        return "CALL"
        
    return None


def check_setup_2(df):
    """ Setup 2: Support Breakout (PUT) - Strict & Mojbot """
    if len(df) < 10: return None
    
    # Support Level Calculation (Rolling Low)
    sup = df['low'].iloc[:-2].rolling(window=20, min_periods=5).min().iloc[-1]
    
    c1 = df.iloc[-2]  # 1no Green Candle (Support Touch and Close Above)
    c2 = df.iloc[-1]  # 2no Red Breakout Candle (Support Break and Close Below)
    
    # 1no Green candle rules: Close > Open (Green), Low touches or goes below support, but Close > Support
    is_c1_green = c1['close'] > c1['open']
    c1_touches_sup = c1['low'] <= sup * 1.005 and c1['close'] > sup
    
    # 2no Red candle rules: Close < Open (Red), and Close breaks below support
    is_c2_red = c2['close'] < c2['open']
    c2_breaks_sup = c2['close'] < sup
    
    if is_c1_green and c1_touches_sup and is_c2_red and c2_breaks_sup:
        return "PUT"
        
    return None
    
