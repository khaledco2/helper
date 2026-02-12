import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# 1. تحسين الأداء: تعريف المصفوفات خارج اللوب (نصيحتك رقم 2)
LOWER = np.array([35, 60, 60], dtype=np.uint8) # نطاق الأخضر/السماوي
UPPER = np.array([105, 255, 255], dtype=np.uint8)

# إعدادات التحكم
SENSITIVITY = 0.8  # تقليل الحساسية ليكون مساعداً لا معيقاً
SMOOTHING = 0.4
is_active = False

ctypes.windll.shcore.SetProcessDpiAwareness(1)

def run_optimized_assistant():
    global is_active
    sct = mss()
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    monitor = {"top": h//2 - 30, "left": w//2 - 30, "width": 60, "height": 60}
    
    last_toggle_check = 0 # (نصيحتك رقم 3)

    print("--- [ Optimized Engine: High Performance ] ---")

    while True:
        current_time = time.time()
        
        # فحص حالة التفعيل كل 100ms لتقليل استهلاك CPU (نصيحتك رقم 3)
        if current_time - last_toggle_check > 0.1:
            if keyboard.is_pressed('f3'): is_active = True
            if keyboard.is_pressed('f4'): is_active = False
            last_toggle_check = current_time

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            
            # تحويل الألوان مرة واحدة فقط (نصيحتك رقم 1)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # MSS تعطي BGRA دائماً
            hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)
            
            # إنشاء الماسك
            mask = cv2.inRange(hsv, LOWER, UPPER)
            
            # تنظيف الضوضاء (نصيحتك رقم 5)
            mask = cv2.erode(mask, None, iterations=1)
            mask = cv2.dilate(mask, None, iterations=1)
            
            M = cv2.moments(mask)
            if M["m00"] > 15: # تجاهل البكسلات المتناثرة
                cY = int(M["m01"] / M["m00"])
                diff_y = (cY - 30)
                
                if diff_y > 1:
                    pull = (diff_y * SENSITIVITY) * SMOOTHING
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
        
        # تقليل استهلاك الطاقة (نصيحتك رقم 4)
        time.sleep(0.01)

if __name__ == "__main__":
    run_optimized_assistant()
