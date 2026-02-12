import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات البصمة اللونية بناءً على صورك ---
SENSITIVITY = 1.6  # قوة السحب المثالية لسكوباتك
is_active = False
ctypes.windll.shcore.SetProcessDpiAwareness(1)

def run_vision_precision():
    global is_active
    sct = mss()
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    
    # منطقة مسح مركزة جداً حول علامة السكوب
    monitor = {"top": h//2 - 40, "left": w//2 - 40, "width": 80, "height": 80}

    print("--- [ Vision Precision Mode: Cyan & Green Tracking ] ---")
    win32api.Beep(1000, 200)

    while True:
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            # تحويل الصورة لنظام HSV لتمكين عزل الألوان التي أرسلتها
            hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)
            
            # 1. نطاق اللون السماوي (Cyan) لصورك (4x & Dot)
            lower_cyan = np.array([80, 100, 100])
            upper_cyan = np.array([100, 255, 255])
            mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
            
            # 2. نطاق اللون الأخضر (Green) لصورك (2x & 3x)
            lower_green = np.array([40, 100, 100])
            upper_green = np.array([75, 255, 255])
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            
            # دمج القناعين للبحث عن أي منهما
            combined_mask = cv2.bitwise_or(mask_cyan, mask_green)
            
            # البحث عن مركز العلامة
            M = cv2.moments(combined_mask)
            if M["m00"] > 5: # إذا وجد العلامة الملونة
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # حساب الإزاحة عن المركز (40 هو منتصف الـ 80)
                diff_y = (cY - 40)
                
                if abs(diff_y) > 1: # إذا تحركت العلامة للأعلى
                    pull = diff_y * SENSITIVITY
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
            
            # حفظ الفريم الحالي كمرجع للسرعة
            prev_mask = combined_mask
        else:
            time.sleep(0.01)

        time.sleep(0.001)

if __name__ == "__main__":
    run_vision_precision()
