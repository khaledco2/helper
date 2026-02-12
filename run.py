import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات صياد العلامات ---
SENSITIVITY = 1.4       # قوة سحب موزونة للسكوبات
is_active = False

# ضبط توافق الشاشة
ctypes.windll.shcore.SetProcessDpiAwareness(1)

def run_reticle_logic():
    global is_active
    sct = mss()
    
    # الحصول على أبعاد الشاشة
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    
    # منطقة مسح صغيرة جداً في السنتر (حيث توجد علامة السكوب)
    # 60x60 بكسل كافية جداً لاصطياد الرد دوت
    monitor = {"top": h//2 - 30, "left": w//2 - 30, "width": 60, "height": 60}

    print("--- [ Reticle Hunter Active: Red Dot, 2x, 3x, 4x ] ---")
    win32api.Beep(1000, 200)

    while True:
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)
            
            # --- السر: البحث عن اللون الأحمر والأخضر الصارخ (علامات السكوب) ---
            # نطاق اللون الأحمر
            lower_red = np.array([0, 120, 70])
            upper_red = np.array([10, 255, 255])
            mask_red = cv2.inRange(hsv, lower_red, upper_red)
            
            # نطاق اللون الأخضر (للعلامات الخضراء)
            lower_green = np.array([36, 100, 100])
            upper_green = np.array([86, 255, 255])
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            
            # دمج العلامات مع حواف السكوب (3x, 4x)
            final_mask = cv2.bitwise_or(mask_red, mask_green)
            
            # إذا لم يجد ألواناً (مثل سكوب 4x الأسود)، نستخدم كشف الحواف للهيكل الداخلي
            if cv2.countNonZero(final_mask) < 10:
                gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                final_mask = cv2.Canny(gray, 50, 150)

            if 'prev_mask' in locals():
                diff = cv2.absdiff(prev_mask, final_mask)
                M = cv2.moments(diff)
                
                if M["m00"] > 40:
                    move_y = (M["m01"] / M["m00"] - 30)
                    pull = move_y * SENSITIVITY
                    if abs(pull) > 0.5:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
            
            prev_mask = final_mask
        else:
            if 'prev_mask' in locals(): del prev_mask
            time.sleep(0.01)

        time.sleep(0.002)

if __name__ == "__main__":
    run_reticle_logic()
