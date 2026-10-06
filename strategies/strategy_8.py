import time

class QuotexStrategy 8:
    def __init__(self):
        self.green_streak = 0
        self.martingale_step = 1
        self.is_recovering = False

    def analyze_candle(self, candle_color):
        """
        candle_color: 'RED' othoba 'GREEN' input dite hobe.
        Output return korbe: Signal ('RED' othoba 'WAIT') ebong bortoman step.
        """
        candle_color = candle_color.upper()
        signal = "WAIT"

        if self.is_recovering:
            # 7-ti green paur por red signal dewa hoyeche, ekhon result check kora hocche
            if candle_color == 'RED':
                print(f"[{time.strftime('%H:%M:%S')}] Result: RED (WIN!) 🎉 | Step: {self.martingale_step}")
                print("--> Strategy safol! Reset kora hocche, notun kore 7-ti green khoja shuru...\n")
                
                # Win howar por sob reset
                self.green_streak = 0
                self.martingale_step = 1
                self.is_recovering = False
                signal = "WAIT"
            else:
                # Jodi candle-ti green hoy (loss), tobe porobortir jonno abar red signal dite hobe ebong step barate hobe
                self.martingale_step += 1
                signal = "RED"
                print(f"[{time.strftime('%H:%M:%S')}] Result: GREEN (LOSS) ❌ | Poroborti signal: **RED** | Notun martingale step: {self.martingale_step}")
        
        else:
            # Swabhavik obostha: 7-ti green candle khoja
            if candle_color == 'GREEN':
                self.green_streak += 1
                print(f"[{time.strftime('%H:%M:%S')}] Green candle dekha geche. Dharabahikota: {self.green_streak}/7")
                
                if self.green_streak == 7:
                    self.is_recovering = True
                    signal = "RED"
                    print(f"--> 7-ti green purno hoyeche! Prothom signal: **RED** (Step: {self.martingale_step})\n")
            else:
                # Majhkhane red asle green counter reset hoye jabe
                if self.green_streak > 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Red candle asay green count reset holo. (Ager count chilo: {self.green_streak})")
                self.green_streak = 0
                signal = "WAIT"

        return signal, self.martingale_step


# --- Test korar jonno demo simulation ---
if __name__ == "__main__":
    bot = QuotexStrategyGreenSeven()
    
    # Demo data: Porpor 7-ti green (8 tomo nambare prothom red signal dibe)
    market_candles = ['GREEN'] * 7 + ['RED']
    
    print("=== Quotex Strategy (7 Green -> Red Logic) Simulation Shuru ===\n")
    
    for i, color in enumerate(market_candles, 1):
        print(f"--- Candle #{i} ({color}) ---")
        current_signal, step = bot.analyze_candle(color)
        print(f"Output signal: {current_signal} | Martingale step: {step}\n")
        time.sleep(0.5)
        
