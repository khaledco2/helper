import cv2
import numpy as np
import time
import keyboard
import ctypes
import pydirectinput
from mss import mss

# --- الإعدادات الفنية ---
LOWER = np.array([35, 60, 60], dtype=np.uint8)
UPPER = np.array([105, 255, 255], dtype=np.uint8)

SENSITIVITY = 1.4
SMOOTHING = 0.6
is_active = False

# مصفوفة الأسلحة
weapon_settings = {"AK": 1.5, "M4": 1.1}
current_w = "AK"

ctypes.windll.user32.SetProcessDPIAware()

def run_advanced_engine():
    global is_active
    sct = mss()
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)

    # 1️⃣ توسيع منطقة الرصد (ROI)
    # جعلناها 100x100 لتعقب السكوب حتى في الارتداد العنيف
    mon_size = 100
    monitor = {
        "top": screen_h//2 - (mon_size//2), 
        "left": screen_w//2 - (mon_size//2), 
        "width": mon_size, 
        "height": mon_size
    }
    center = mon_size // 2

    print(f"--- [ Engine Active | ROI: {mon_size}x{mon_size} ] ---")

    while True:
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000:
            img = np.array(sct.grab(monitor))
            hsv = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, LOWER, UPPER)
            
            # 3️⃣ تحسين فلترة الهدف (نصيحتك المورفولوجية)
            mask = cv2.erode(mask, None, iterations=1)
            mask = cv2.dilate(mask, None, iterations=1)

            M = cv2.moments(mask)
            # فحص إذا كان هناك هدف كافٍ للرصد (تجنب الضوضاء)
            if M["m00"] > 25: 
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # 2️⃣ تصحيح اتجاه Y وحساب المسافة عن المركز
                diff_x = cX - center
                diff_y = cY - center

                # 4️⃣ تجنب صفر الحركة (Zero Movement Prevention)
                # لا نرسل حركة إلا إذا تجاوز الفرق حداً معيناً لمنع الارتعاش
                if abs(diff_x) > 1 or abs(diff_y) > 1:
                    pull_x = int(diff_x * weapon_settings[current_w] * SMOOTHING)
                    pull_y = int(diff_y * weapon_settings[current_w] * SMOOTHING)
                    
                    # إرسال الحركة عبر Hardware Emulation
                    pydirectinput.moveRel(pull_x, pull_y, relative=True)

        time.sleep(0.001)

if __name__ == "__main__":
    run_advanced_engine()
