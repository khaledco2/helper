import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- الإعدادات الموزونة بعناية ---
SENSITIVITY = 1.4       # تقليل القوة قليلاً لضمان عدم الهروب للأسفل
THRESHOLD_VAL = 35      # تجاهل الاهتزازات البسيطة لزيادة الثبات
is_active = False

def run_fine_tuned():
    global is_active
    sct = mss()
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 40, 
               "left": win32api.GetSystemMetrics(0)//2 - 40, 
               "width": 80, "height": 80}

    print("--- [ Fine-Tuned Original Logic ] ---")
    win32api.Beep(1000, 200)

    while True:
        # F3 لتفعيل - F4 لإيقاف
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            if 'prev_gray' in locals():
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, THRESHOLD_VAL, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                if M["m00"] > 60:
                    # حساب السحب المباشر
                    pull = (M["m01"] / M["m00"] - 40) * SENSITIVITY
                    
                    # تنفيذ السحب فقط إذا كانت الحركة واضحة
                    if abs(pull) > 1:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
            
            prev_gray = gray
        else:
            if 'prev_gray' in locals(): del prev_gray
            time.sleep(0.01)

        time.sleep(0.008) # تقليل التأخير قليلاً لزيادة الاستجابة

if __name__ == "__main__":
    run_fine_tuned()
