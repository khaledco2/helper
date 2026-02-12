import win32api
import win32con
import pydirectinput
import keyboard
import time
import os
import random
import ctypes
from random import randint, uniform

# إعدادات الحماية وتوافق الشاشة
ctypes.windll.shcore.SetProcessDpiAwareness(1)
pydirectinput.FAILSAFE = False # لمنع توقف السكربت عند وصول الماوس للزاوية

# --- المتغيرات الأساسية ---
version = "3.0 PRO"
is_active = False
current_weapon = "AK"
# مصفوفة الحساسية (يمكنك تعديل القيم هنا لتناسبك)
# القيمة الأولى: سحب عمودي (Y)، القيمة الثانية: تنعيم (Smoothing)
weapons = {
    "AK": [12, 0.6], 
    "M4": [8, 0.5],
    "SMG": [5, 0.4]
}

def draw_ui():
    os.system('cls' if os.name == 'nt' else 'clear')
    status = "ON" if is_active else "OFF"
    print(f"==============================================")
    print(f"   No-Recoil Hardware Emulator V{version}")
    print(f"==============================================")
    print(f" STATUS: {status} | WEAPON: {current_weapon}")
    print(f"----------------------------------------------")
    print(f" F3: ACTIVATE | F4: DEACTIVATE")
    print(f" NUM1: AK | NUM2: M4 | NUM3: SMG")
    print(f"----------------------------------------------")
    print(f" [+] Real-time Y-Correction: ACTIVE")
    print(f" [+] Zero-Movement Deadzone: ACTIVE")
    print(f"==============================================")

def run_script():
    global is_active, current_weapon
    draw_ui()
    
    last_ui_update = time.time()

    while True:
        # تحديث الواجهة عند التغيير
        if time.time() - last_ui_update > 0.5:
            # تم اختصار التحديث لتقليل استهلاك CPU
            last_ui_update = time.time()

        # مفاتيح التحكم
        if keyboard.is_pressed('f3'): 
            if not is_active:
                is_active = True
                win32api.Beep(1000, 100)
                draw_ui()
        if keyboard.is_pressed('f4'): 
            if is_active:
                is_active = False
                win32api.Beep(500, 100)
                draw_ui()

        # اختيار السلاح
        if keyboard.is_pressed('1'): current_weapon = "AK"; draw_ui()
        if keyboard.is_pressed('2'): current_weapon = "M4"; draw_ui()
        if keyboard.is_pressed('3'): current_weapon = "SMG"; draw_ui()

        # منطق السحب (يعمل فقط عند الضغط على زر الماوس الأيسر والسكربت مفعل)
        if is_active and win32api.GetAsyncKeyState(0x01) & 0x8000:
            val_y = weapons[current_weapon][0]
            smoothing = weapons[current_weapon][1]

            # 1️⃣ إضافة عشوائية بسيطة لمنع كشف السكربت (Humanization)
            random_factor = uniform(-1.5, 1.5)
            
            # 2️⃣ حساب السحب النهائي مع تصحيح اتجاه Y
            # السحب للأسفل يكون بقيمة موجبة في pydirectinput
            pull_y = int((val_y + random_factor) * smoothing)

            # 3️⃣ تجنب صفر الحركة (لا نرسل أوامر إذا كان السحب تافهاً)
            if pull_y > 0:
                # 4️⃣ استخدام DirectInput لتخطي حماية اللعبة (Kernel Level)
                pydirectinput.moveRel(0, pull_y, relative=True)
            
            # سرعة التكرار متوافقة مع سرعة إطلاق النار (Rate of Fire)
            time.sleep(0.01) 

        time.sleep(0.001)

if __name__ == "__main__":
    try:
        run_script()
    except KeyboardInterrupt:
        print("\n[!] Script Stopped.")
