import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# إعدادات الألوان (بصمتك الخاصة)
LOWER = np.array([35, 60, 60], dtype=np.uint8)
UPPER = np.array([105, 255, 255], dtype=np.uint8)

# إعدادات التحكم المحسنة
SMOOTHING = 0.4
is_active = False

# مصفوفة الأسلحة الخاصة بك
weapon_sensitivity = {"AK": 1.3, "M4": 1.0, "Pistol": 0.6}
current_weapon = "AK"

# إجبار الويندوز على قراءة الأبعاد الحقيقية (حل مشكلة عدم العمل)
ctypes.windll.user32.SetProcessDPIAware()

def run_final_engine():
    global is_active
    sct = mss()
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    
    # توسيع منطقة المسح لضمان عدم ضياع السكوب عند الارتداد القوي
    monitor = {"top": h//2 - 40, "left": w//2 - 40, "width": 80, "height": 80}
    center = 40 # نقطة المنتصف الجديدة

    print(f"--- [ Engine Ready | Res: {w}x{h} ] ---")

    while True:
        # فحص سريع للمفاتيح
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط ومعالجة
            img = np.array(sct.grab(monitor))
            hsv = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, LOWER, UPPER)
            
            # تنظيف القناع (نصيحتك السابقة)
            mask = cv2.erode(mask, None, iterations=1)
            mask = cv2.dilate(mask, None, iterations=1)

            # تتبع الكتلة اللونية (أسرع وأدق للسكوبات)
            M = cv2.moments(mask)
            if M["m00"] > 15:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # حساب المسافة عن المركز
                diff_x = cX - center
                diff_y = cY - center

                # السحب بناءً على السلاح المختار
                pull_x = int(diff_x * weapon_sensitivity[current_weapon] * SMOOTHING)
                pull_y = int(diff_y * weapon_sensitivity[current_weapon] * SMOOTHING)

                # إرسال الحركة
                if abs(pull_x) > 0 or abs(pull_y) > 0:
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, pull_x, pull_y, 0, 0)

        time.sleep(0.001)

if __name__ == "__main__":
    run_final_engine()
