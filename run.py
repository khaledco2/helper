import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات الاحتراف النهائية ---
SENSITIVITY = 1.35      # تقليل طفيف لإنهاء الإزاحة
DEADZONE = 5            # منطقة ميتة لتجاهل الحركات غير الضرورية
is_active = False

# ضبط دقة الشاشة
ctypes.windll.shcore.SetProcessDpiAwareness(1)

def run_pure_motion_logic():
    global is_active
    sct = mss()
    
    width = win32api.GetSystemMetrics(0)
    height = win32api.GetSystemMetrics(1)
    
    # منطقة مسح مركزة جداً (Center-Lock)
    monitor = {"top": height//2 - 50, 
               "left": width//2 - 50, 
               "width": 100, "height": 100}

    print("--- [ Frequency Stability Mode Active ] ---")
    win32api.Beep(1000, 200)

    while True:
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        # شرط مزدوج: التفعيل + الضغط على الماوس
        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            
            # تحسين الصورة ليرى "الجدار" كأنه جسم صلب
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            if 'prev_gray' in locals():
                # كشف الفرق بين الفريمات
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                
                # حساب مركز الكتلة للحركة
                M = cv2.moments(thresh)
                
                if M["m00"] > 100: # زيادة الحساسية لبدء الحركة
                    move_y = (M["m01"] / M["m00"] - 50)
                    
                    # الفلتر: إذا كانت الحركة صغيرة جداً (بعد انتهاء الرصاص) لا تسحب
                    if abs(move_y) > DEADZONE:
                        pull = move_y * SENSITIVITY
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
                
            prev_gray = gray
        else:
            # تصفير الذاكرة فوراً عند رفع الإصبع لمنع الإزاحة
            if 'prev_gray' in locals():
                del prev_gray
            time.sleep(0.01)

        time.sleep(0.001)

if __name__ == "__main__":
    run_pure_motion_logic()
