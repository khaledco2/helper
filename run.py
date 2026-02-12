import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from PIL import ImageGrab

# --- إعدادات القوة والسكوبات ---
BASE_SENSITIVITY = 1.8  # القوة الأساسية للرد دوت
scope_multiplier = 1.0   # المضاعف الافتراضي
is_running = False

def start_engine():
    global is_running, scope_multiplier
    
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    mid_x, mid_y = w // 2, h // 2
    ROI = (mid_x - 30, mid_y - 30, mid_x + 30, mid_y + 30)
    
    print(f"--- نظام السكوبات الذكي نشط ---")
    print("F3: تشغيل | F4: إيقاف")
    print("رقم 1: سكوب (Red Dot) | رقم 2: سكوب (2X) | رقم 3: سكوب (3X) | رقم 4: سكوب (4X)")

    prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))

    while True:
        # تبديل القوة حسب السكوب المستخدم
        if keyboard.is_pressed('1'): scope_multiplier = 1.0; print("Mode: Red Dot")
        if keyboard.is_pressed('2'): scope_multiplier = 1.6; print("Mode: Scope 2X")
        if keyboard.is_pressed('3'): scope_multiplier = 2.4; print("Mode: Scope 3X")
        if keyboard.is_pressed('4'): scope_multiplier = 3.5; print("Mode: Scope 4X")

        if keyboard.is_pressed('f3'): is_running = True
        if keyboard.is_pressed('f4'): is_running = False

        if is_running and win32api.GetAsyncKeyState(0x01) < 0:
            curr_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
            
            # خوارزمية محسنة لتقليل الاهتزاز (Smoothing)
            diff = cv2.absdiff(prev_frame, curr_frame)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            M = cv2.moments(thresh)
            if M["m00"] > 80:
                # حساب القوة النهائية بناءً على السكوب المختار
                final_pull = int(BASE_SENSITIVITY * scope_multiplier * 6)
                
                # تقسيم الحركة لنبضات صغيرة جداً لتقليل الاهتزاز (Micro-steps)
                for _ in range(2): 
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, final_pull // 2, 0, 0)
                    time.sleep(0.001)
            
            prev_frame = curr_frame
        else:
            if time.time() % 0.2 < 0.01:
                prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
        
        time.sleep(0.002)

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        start_engine()
