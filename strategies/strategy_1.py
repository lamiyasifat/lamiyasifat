import time

class QuotexStrategy:
    def __init__(self):
        self.red_streak = 0
        self.martingale_step = 1
        self.is_recovering = False

    def analyze_candle(self, candle_color):
        """
        candle_color: 'RED' অথবা 'GREEN' ইনপুট দিতে হবে।
        আউটপুট রিটার্ন করবে: সিগন্যাল ('GREEN' অথবা 'WAIT') এবং বর্তমান স্টেপ।
        """
        candle_color = candle_color.upper()
        signal = "WAIT"

        if self.is_recovering:
            # আমরা অলরেডি সিগন্যাল দিয়েছি, এখন দেখতে হবে ক্যান্ডেলের রেজাল্ট কী হলো
            if candle_color == 'GREEN':
                print(f"[{time.strftime('%H:%M:%S')}] রেজাল্ট: GREEN (WIN!) 🎉 | স্টেপ: {self.martingale_step}")
                print("--> স্ট্র্যাটেজি সফল! রিসেট করা হচ্ছে, নতুন করে ৫টি রেড খোঁজা শুরু...\n")
                
                # উইন হওয়ার পর সব রিসেট
                self.red_streak = 0
                self.martingale_step = 1
                self.is_recovering = False
                signal = "WAIT"
            else:
                # যদি ক্যান্ডেলটি রেড হয় (লস), তবে পরেরটার জন্য আবার গ্রিন সিগন্যাল দিতে হবে এবং স্টেপ বাড়াতে হবে
                self.martingale_step += 1
                signal = "GREEN"
                print(f"[{time.strftime('%H:%M:%S')}] রেজাল্ট: RED (LOSS) ❌ | পরবর্তী সিগন্যাল: **GREEN** | নতুন মার্টিংগেল স্টেপ: {self.martingale_step}")
        
        else:
            # স্বাভাবিক অবস্থা: ৫টি রেড ক্যান্ডেল খোঁজা
            if candle_color == 'RED':
                self.red_streak += 1
                print(f"[{time.strftime('%H:%M:%S')}] রেড ক্যান্ডেল দেখা গেছে। ধারাবাহিকতা: {self.red_streak}/5")
                
                if self.red_streak == 5:
                    self.is_recovering = True
                    signal = "GREEN"
                    print(f"--> ৫টি রেড পূর্ণ হয়েছে! প্রথম সিগন্যাল: **GREEN** (স্টেপ: {self.martingale_step})\n")
            else:
                # মাঝখানে গ্রিন আসলে রেড কাউন্টার রিসেট হয়ে যাবে
                if self.red_streak > 0:
                    print(f"[{time.सुनो('%H:%M:%S')}] গ্রিন ক্যান্ডেল আসায় রেড কাউন্ট রিসেট হলো। (বর্তমান কাউন্ট ছিল: {self.red_streak})")
                self.red_streak = 0
                signal = "WAIT"

        return signal, self.martingale_step


# --- টেস্ট করার জন্য ডেমো সিমুলেশন ---
if __name__ == "__main__":
    bot = QuotexStrategy()
    
    # এখানে ডেমো ডেটা দেওয়া হলো:
    # ১-৫: পরপর ৫টি রেড (৫ম নাম্বারে প্রথম গ্রিন সিগন্যাল দিবে)
    # ৬: আবার রেড (তাই লস, ৭ নম্বরের জন্য আবার গ্রিন সিগন্যাল দিবে এবং স্টেপ ২ হবে)
    # ৭: আবার রেড (তাই লস, ৮ নম্বরের জন্য আবার গ্রিন সিগন্যাল দিবে এবং স্টেপ ৩ হবে)
    # ৮: গ্রিন (উইন! রিসেট হয়ে যাবে)
    
    market_candles = ['RED', 'RED', 'RED', 'RED', 'RED', 'RED', 'RED', 'GREEN']
    
    print("=== কোটেক্স স্ট্র্যাটেজি সিমুলেশন শুরু ===\n")
    
    for i, color in enumerate(market_candles, 1):
        print(f"--- ক্যান্ডেল #{i} ({color}) ---")
        current_signal, step = bot.analyze_candle(color)
        print(f"আউটপুট সিগন্যাল: {current_signal} | মার্টিংগেল স্টেপ: {step}\n")
        time.sleep(0.5)
