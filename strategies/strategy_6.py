import time

class QuotexStrategy6:
    def __init__(self):
        self.red_streak = 0
        self.martingale_step = 1
        self.is_recovering = False

    def analyze_candle(self, candle_color):
        candle_color = candle_color.upper()
        signal = "WAIT"

        if self.is_recovering:
            if candle_color == 'GREEN':
                print(f"[{time.strftime('%H:%M:%S')}] Result: GREEN (WIN!) 🎉 | Step: {self.martingale_step}")
                print("--> Strategy successful! Resetting...\n")
                self.red_streak = 0
                self.martingale_step = 1
                self.is_recovering = False
                signal = "WAIT"
            else:
                self.martingale_step += 1
                signal = "GREEN"
                print(f"[{time.strftime('%H:%M:%S')}] Result: RED (LOSS) ❌ | Next Signal: **GREEN** | Martingale Step: {self.martingale_step}")
        
        else:
            if candle_color == 'RED':
                self.red_streak += 1
                print(f"[{time.strftime('%H:%M:%S')}] Red candle spotted. Streak: {self.red_streak}/15")
                
                if self.red_streak == 15:
                    self.is_recovering = True
                    signal = "GREEN"
                    print(f"--> 15 Reds completed! First Signal: **GREEN** (Step: {self.martingale_step})\n")
            else:
                if self.red_streak > 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Green candle appeared, red streak reset.")
                self.red_streak = 0
                signal = "WAIT"

        return signal, self.martingale_step

# --- Demo Simulation ---
if __name__ == "__main__":
    bot = QuotexStrategy6()  # সঠিক ক্লাস নাম দেওয়া হলো
    market_candles = ['RED'] * 15 + ['GREEN']
    
    print("=== Quotex Strategy 6 (15 Red Logic) Simulation Started ===\n")
    
    for i, color in enumerate(market_candles, 1):
        print(f"--- Candle #{i} ({color}) ---")
        current_signal, step = bot.analyze_candle(color)
        print(f"Output Signal: {current_signal} | Martingale Step: {step}\n")
        time.sleep(0.1)
            
