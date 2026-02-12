import win32api, keyboard, time, ctypes, os
import pydirectinput
from random import uniform
# استيراد ملفك المساعد (يجب أن يكون بجانب السكربت)
import dontExecute 

# إعدادات تخطي الحماية والأداء الأقصى
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
        """تحميل القيم من الذاكرة لتجنب البطء الناتج عن قراءة القرص"""
        try:
            slot_key = "slot1" if self.current_slot == 1 else "slot2"
            weapon_name = dontExecute.getConfig("Settings", slot_key)
            vals = dontExecute.getRecoilValues(weapon_name)
            self.recoil_values = [int(vals[0]), int(vals[1])]
            # نغمة صوتية عند تبديل السلاح
            win32api.Beep(1200 if self.current_slot == 1 else 1500, 100)
        except:
            pass

    def run(self):
        # التأكد من جاهزية ملف الإعدادات
        if not os.path.exists('config.cfg'):
            dontExecute.writeConfig()
        
        self.load_weapon_data()
        print("--- SILENT ENGINE RUNNING (NO OVERLAY) ---")
        print("F3: Toggle | 1 & 2: Switch Weapons")

        while True:
            # 1. مفتاح التفعيل (F3) - صامت لا يظهر فوق اللعبة
            if keyboard.is_pressed('f3'):
                self.rcs_active = not self.rcs_active
                # نغمة حادة للتفعيل، غليظة للإيقاف
                win32api.Beep(1000 if self.rcs_active else 500, 200)
                time.sleep(0.3)

            # 2. تبديل الأسلحة (1 أو 2)
            if keyboard.is_pressed('1') and self.current_slot != 1:
                self.current_slot = 1
                self.load_weapon_data()
            elif keyboard.is_pressed('2') and self.current_slot != 2:
                self.current_slot = 2
                self.load_weapon_data()

            # 3. منطق السحب (إطلاق النار)
            if self.rcs_active and win32api.GetAsyncKeyState(0x01) & 0x8000:
                # التحقق من نافذة اللعبة باستخدام دالتك
                if str(dontExecute.activeWindow()) == str(dontExecute.neededWindow(self.process_name)):
                    count = 0
                    while win32api.GetAsyncKeyState(0x01) & 0x8000:
                        # اختيار القيمة (أول 11 طلقة أو ما بعدها)
                        base_y = self.recoil_values[0] if count < 11 else self.recoil_values[1]
                        
                        # إضافة "فلترة الهدف" (Humanization)
                        jitter = uniform(-1.2, 1.2)
                        final_y = int(round(base_y + jitter))

                        # 4. تصحيح Y وتجنب صفر الحركة
                        if final_y > 1:
                            # استخدام محاكي الهاردوير DirectInput
                            pydirectinput.moveRel(0, final_y, relative=True)
                        
                        count += 1
                        time.sleep(0.09) # سرعة متوافقة مع معدل إطلاق النار

            time.sleep(0.005)

if __name__ == "__main__":
    scr = SilentAntiRecoil()
    scr.run()
