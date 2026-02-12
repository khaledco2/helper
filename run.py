import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات الترويض والهدوء ---
SENSITIVITY = 0.6      # خفضنا القوة للنصف لضمان عدم القفز للأسفل
SMOOTHING = 0.15       # تنعيم فائق (كلما قل الرقم أصبح السحب أنعم كالزيت)
DEADZONE = 2.0         # يتجاهل أي حركة بكسلات صغيرة جداً لمنع الارتجاف
is_active = False

def run_calm_system():
    global is_active
    sct = mss()
    
    # منطقة مسح مركزية متوازنة
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 40, 
               "left": win32api.GetSystemMetrics(0)//2 - 40, 
               "width": 80, "height": 80}

    print("--- [ Calm & Smooth System Active ] ---")
    win32api.Beep(1000, 200)

    last_pull = 0

    while True:
        if keyboard.is_pressed('f3') and not is_active:
            is_active = True
            win32api.Beep(1200, 100)
        if keyboard.is_pressed('f4') and is_active:
            is_active = False
            win32api.Beep(400, 200)

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط الشاشة
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            if 'prev_gray' in locals():
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, 35, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                if M["m00"] > 60:
                    # حساب الإزاحة الفعلية
                    raw_y = (M["m01"] / M["m00"] - 40)
                    
                    if abs(raw_y) > DEADZONE:
                        # تطبيق معادلة التنعيم
                        target_pull = raw_y * SENSITIVITY
                        current_pull = last_pull + (target_pull - last_pull) * SMOOTHING
                        
                        # تنفيذ الحركة
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(current_pull), 0, 0)
                        last_pull = current_pull
                else:
                    last_pull = 0
            
            prev_gray = gray
        else:
            last_pull = 0
            time.sleep(0.01)

        time.sleep(0.002) # زيادة بسيطة في التأخير لراحة المعالج ومنع الجنون

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        run_calm_system()
    else:
        print("Run as Admin!")
