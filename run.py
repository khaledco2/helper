import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات تخطي العقبات ---
SENSITIVITY = 1.8       # قوة سحب واضحة
is_active = False

# ضمان توافق الإحداثيات مع الـ Scaling الخاص بويندوز
ctypes.windll.shcore.SetProcessDpiAwareness(1)

def run_global_logic():
    global is_active
    sct = mss()
    
    # الحصول على أبعاد الشاشة الحقيقية
    width = win32api.GetSystemMetrics(0)
    height = win32api.GetSystemMetrics(1)
    
    # منطقة مسح أكبر قليلاً لضمان عدم الضياع
    monitor = {"top": height//2 - 60, 
               "left": width//2 - 60, 
               "width": 120, "height": 120}

    print(f"--- [ Global Logic Active - Screen: {width}x{height} ] ---")
    win32api.Beep(1000, 200)

    while True:
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط الشاشة وتحسين التباين
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            # تقوية الفرق في الألوان لجعل الجدار "مرئياً" للسكربت
            gray = cv2.equalizeHist(gray) 
            
            if 'prev_gray' in locals():
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                if M["m00"] > 40:
                    # سحب مباشر وقوي
                    pull = (M["m01"] / M["m00"] - 60) * SENSITIVITY
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
            
            prev_gray = gray
        else:
            if 'prev_gray' in locals(): del prev_gray
            time.sleep(0.01)

        time.sleep(0.002)

if __name__ == "__main__":
    run_global_logic()
