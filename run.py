import win32api, keyboard, time, ctypes, os
import pydirectinput
from random import uniform
# استيراد ملفك المساعد (تأكد أنه في نفس المجلد)
import dontExecute 

# إعدادات السرعة القصوى وتخطي الحماية
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False
ctypes.windll.user32.SetProcessDPIAware()

class SilentAntiRecoil:
    def __init__(self):
        self.rcs_active = False
        self.current_slot = 1
        self.process_name = "TslGame" # PUBG
        self.recoil_values = [0, 0]
        
    def load_weapon_data(self):
        """تحميل القيم من ملفك config.cfg إلى الذاكرة"""
        try:
            slot_key = "slot1" if self.current_slot == 1 else "slot2"
            weapon_name = dontExecute.getConfig("Settings", slot_key)
            vals = dontExecute.getRecoilValues(weapon_name)
            self.recoil_values = [int(vals[0]), int(vals[1])]
            # تنبيه صوتي عند تغيير السلاح (نغمتين للسلاح 2، نغمة للسلاح 1)
            for _ in range(self.current_slot):
                win32api.Beep(1200, 100)
                time.sleep(0.05)
        except:
            pass

    def run(self):
        print("--- [ SCRIPT ACTIVE - SILENT MODE ] ---")
        print("F3: Toggle RCS | 1 & 2: Switch Slots")
        
        # التأكد من وجود ملف الإعدادات
        if not os.path.exists('config.cfg'):
            dontExecute.writeConfig()
        
        self.load_weapon_data()

        while True:
            # 1. تفعيل/إيقاف السكربت (F3)
            if keyboard.is_pressed('f3'):
                self.rcs_active = not self.rcs_active
                win32api.Beep(1000 if self.rcs_active else 500, 200)
                time.sleep(0.3)

            # 2. تبديل الأسلحة (1 أو 2)
            if keyboard.is_pressed('1') and self.current_slot != 1:
                self.current_slot = 1
                self.load_weapon_data()
            elif keyboard.is_pressed('2') and self.current_slot != 2:
                self.current_slot = 2
                self.load_weapon_data()

            # 3. منطق السحب (أثناء الضغط على الماوس الأيسر)
            if self.rcs_active and win32api.GetAsyncKeyState(0x01) & 0x8000:
                # التحقق أن اللعبة هي النافذة النشطة (باستخدام دالتك)
                if str(dontExecute.activeWindow()) == str(dontExecute.neededWindow(self.process_name)):
                    count = 0
                    while win32api.GetAsyncKeyState(0x01) & 0x8000:
                        # جلب القيمة (أول 11 طلقة أو ما بعدها)
                        base_y = self.recoil_values[0] if count < 11 else self.recoil_values[1]
                        
                        # إضافة عشوائية بسيطة (Humanization)
                        jitter = uniform(-1.1, 1.1)
                        final_y = int(round(base_y + jitter))

                        # تصحيح Y وتجنب صفر الحركة
                        if final_y > 1:
                            pydirectinput.moveRel(0, final_y, relative=True)
                        
                        count += 1
                        time.sleep(0.09) # سرعة سحب متوافقة مع الأسلحة الآلية

            time.sleep(0.005)

if __name__ == "__main__":
    scr = SilentAntiRecoil()
    scr.run()
