def check_setup_2(df):
    """ Setup 2: Support Breakout (PUT) - Updated """
    if len(df) < 6: return None
    
    # Support Level Calculation (Rolling Low)
    sup = df['low'].iloc[:-2].rolling(window=20, min_periods=5).min().iloc[-1]
    
    c1 = df.iloc[-2]  # 1no Green Candle (Seba / Support Touch and Close Above)
    c2 = df.iloc[-1]  # 2no Red Breakout Candle (Support Break and Close Below)
    
    # 1no Green candle rules: Close > Open (Green), Low touches or goes below support, but Close > Support
    is_c1_green = c1['close'] > c1['open']
    c1_touches_sup = c1['low'] <= sup and c1['close'] > sup
    
    # 2no Red candle rules: Close < Open (Red), Open >= support, and Close breaks below support
    is_c2_red = c2['close'] < c2['open']
    c2_breaks_sup = c2['close'] < sup
    
    if is_c1_green and c1_touches_sup and is_c2_red and c2_breaks_sup:
        return "PUT"
    return None
    
