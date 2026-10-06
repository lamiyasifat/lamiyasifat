import time

class QuotexStrategy 9:
    def __init__(self):
        self.green_streak = 0
        self.martingale_step = 1
        self.is_recovering = False

    def analyze_candle(self, candle_color):
        """
        candle_color: 'RED' অথবা 'GREEN' ইনপুট দিতে হবে।
        আউটপুট রিটার্ন করবে: সিগন্যাল ('RED' অথবা 'WAIT') এবং বর্তমান স্টেপ।
        """
        candle_color = candle_color.upper()
        signal = "WAIT"

        if self.is_recovering:
            # ৯টি গ্রিন পাওয়ার পর রেড সিগন্যাল দেওয়া হয়েছে, এখন রেজাল্ট চেক করা হচ্ছে
            if candle_color == 'RED':
                print(f"[{time.strftime('%H:%M:%S')}] রেজাল্ট: RED (WIN!) 🎉 | স্টেপ: {self.martingale_step}")
                print("--> স্ট্র্যাটেজি সফল! রিসেট করা হচ্ছে, নতুন করে ৯টি গ্রিন খোঁজা শুরু...\n")
                
                # উইন হওয়ার পর সব রিসেট
                self.green_streak = 0
                self.martingale_step = 1
                self.is_recovering = False
                signal = "WAIT"
            else:
                # যদি ক্যান্ডেলটি গ্রিন হয় (লস), তবে পরেরটার জন্য আবার রেড সিগন্যাল দিতে হবে এবং স্টেপ বাড়াতে হবে
                self.martingale_step += 1
                signal = "RED"
                print(f"[{time.strftime('%H:%M:%S')}] রেজাল্ট: GREEN (LOSS) ❌ | পরবর্তী সিগন্যাল: **RED** | নতুন মার্টিংগেল স্টেপ: {self.martingale_step}")
        
        else:
            # স্বাভাবিক অবস্থা: ৯টি গ্রিন ক্যান্ডেল খোঁজা
            if candle_color == 'GREEN':
                self.green_streak += 1
                print(f"[{time.strftime('%H:%M:%S')}] গ্রিন ক্যান্ডেল দেখা গেছে। ধারাবাহিকতা: {self.green_streak}/9")
                
                if self.green_streak == 9:
                    self.is_recovering = True
                    signal = "RED"
                    print(f"--> ৯টি গ্রিন পূর্ণ হয়েছে! প্রথম সিগন্যাল: **RED** (স্টেপ: {self.martingale_step})\n")
            else:
                # মাঝখানে রেড আসলে গ্রিন কাউন্টার রিসেট হয়ে যাবে
                if self.green_streak > 0:
                    print(f"[{time.strftime('%H:%M:%S')}] রেড ক্যান্ডেল আসায় গ্রিন কাউন্ট রিসেট হলো। (আগের কাউন্ট ছিল: {self.green_streak})")
                self.green_streak = 0
                signal = "WAIT"

        return signal, self.martingale_step


# --- টেস্ট করার জন্য ডেমো সিমুলেশন ---
if __name__ == "__main__":
    bot = QuotexStrategyGreenNine()
    
    # ডেমো ডেটা: পরপর ৯টি গ্রিন (১০ম নাম্বারে প্রথম রেড সিগন্যাল দিবে)
    market_candles = ['GREEN'] * 9 + ['RED']
    
    print("=== কোটেক্স স্ট্র্যাটেজি (9 Green -> Red Logic) সিমুলেশন শুরু ===\n")
    
    for i, color in enumerate(market_candles, 1):
        print(f"--- ক্যান্ডেল #{i} ({color}) ---")
        current_signal, step = bot.analyze_candle(color)
        print(f"আউটপুট সিগন্যাল: {current_signal} | মার্টিংগেল স্টেপ: {step}\n")
        time.sleep(0.5)
        
