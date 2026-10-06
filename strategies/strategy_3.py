import time

class QuotexStrategy3:
    def __init__(self):
        self.red_streak = 0
        self.martingale_step = 1
        self.is_recovering = False

    def analyze_candle(self, candle_color):
        candle_color = candle_color.upper()
        signal = "WAIT"

        if self.is_recovering:
            if candle_color == 'GREEN':
                self.red_streak = 0
                self.martingale_step = 1
                self.is_recovering = False
                signal = "WAIT"
            else:
                self.martingale_step += 1
                signal = "GREEN"
        else:
            if candle_color == 'RED':
                self.red_streak += 1
                if self.red_streak == 7:
                    self.is_recovering = True
                    signal = "GREEN"
            else:
                self.red_streak = 0
                signal = "WAIT"

        return signal, self.martingale_step
        
