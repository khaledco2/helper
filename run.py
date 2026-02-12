import mss
import cv2
import numpy as np
import win32api, win32con
import keyboard

# إعدادات متقدمة
SENSITIVITY = 0.4  # تنعيم الحركة
MONITOR_SIZE = 100 # منطقة مسح أكبر قليلاً (100x100)

def start_advanced_engine():
    sct = mss.mss()
    
    # تحديد منطقة المسح في منتصف الشاشة
    scr_w = win32api.GetSystemMetrics(0)
    scr_h = win32api.GetSystemMetrics(1)
    
    region = {
        'top': (scr_h // 2) - (MONITOR_SIZE // 2),
        'left': (scr_w // 2) - (MONITOR_SIZE // 2),
        'width': MONITOR_SIZE,
        'height': MONITOR_SIZE
    }

    print("--- النظام المطور يعمل (F3 للتشغيل / F4 للإيقاف) ---")
    active = False

    while True:
        if keyboard.is_pressed('f3'): active = True
        if keyboard.is_pressed('f4'): active = False

        if active and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط الشاشة بسرعة فائقة
            img = np.array(sct.grab(region))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            
            # كشف النقاط المضيئة أو التغير اللوني (مثلاً الأعداء أو الارتداد)
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # حساب العزوم (Moments) لتحديد مركز الهدف
            M = cv2.moments(thresh)
            if M["m00"] > 0:
                target_x = int(M["m10"] / M["m00"])
                target_y = int(M["m01"] / M["m00"])
                
                # حساب المسافة من مركز الـ ROI (الذي هو 50,50)
                dx = int((target_x - 50) * SENSITIVITY)
                dy = int((target_y - 50) * SENSITIVITY)
                
                # تحريك الفأرة باتجاه الهدف فعلياً وليس للأسفل فقط
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

# ملاحظة: هذا الكود للأغراض التعليمية فقط
