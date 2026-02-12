import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# ===================== إعدادات الألوان =====================
LOWER = np.array([35, 60, 60], dtype=np.uint8)   # نطاق الأخضر/السماوي
UPPER = np.array([105, 255, 255], dtype=np.uint8)

# ===================== إعدادات التحكم =====================
SENSITIVITY = 0.8      # حساسية عامة
SMOOTHING = 0.5        # نعومة الحركة
is_active = False

# حساسية لكل سلاح (يمكنك تعديلها)
weapon_sensitivity = {
    "AK": 1.2,
    "M4": 0.9,
    "Pistol": 0.5
}
current_weapon = "AK"  # اختر السلاح الافتراضي

# ===================== تحسين DPI =====================
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# ===================== الوظيفة الأساسية =====================
def run_optimized_assistant():
    global is_active
    sct = mss()
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    monitor = {"top": h//2 - 20, "left": w//2 - 20, "width": 40, "height": 40}

    last_toggle_check = 0
    print("--- [ Optimized Recoil Controller ] ---")

    while True:
        current_time = time.time()

        # تفعيل/إيقاف السكربت (كل 100ms لتقليل استهلاك CPU)
        if current_time - last_toggle_check > 0.1:
            if keyboard.is_pressed('f3'):
                is_active = True
            if keyboard.is_pressed('f4'):
                is_active = False
            last_toggle_check = current_time

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:  # إذا ضغطت زر الماوس الأيسر
            img = np.array(sct.grab(monitor))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(hsv, LOWER, UPPER)
            mask = cv2.erode(mask, None, iterations=1)
            mask = cv2.dilate(mask, None, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 50:  # تجاهل الأشياء الصغيرة
                    M = cv2.moments(cnt)
                    if M["m00"] > 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        diff_x = cX - 20
                        diff_y = cY - 20

                        # حساب السحب مع الحساسية لكل سلاح
                        pull_x = int(diff_x * weapon_sensitivity[current_weapon] * SMOOTHING)
                        pull_y = int(diff_y * weapon_sensitivity[current_weapon] * SMOOTHING)

                        # تحريك الماوس
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, pull_x, pull_y, 0, 0)

        # تقليل استهلاك المعالج
        time.sleep(0.005)

# ===================== التشغيل =====================
if __name__ == "__main__":
    run_optimized_assistant()
