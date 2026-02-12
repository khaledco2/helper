import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات الثبات المستمر ---
SENSITIVITY = 0.8      # قوة السحب الأساسية
SMOOTHING = 0.2        # درجة النعومة
MIN_DETECTION = 40     # حساسية كشف الحركة (لضمان عدم الانقطاع)
is_active = False

def run_stable_system():
    global is_active
    sct = mss()
    
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 50, 
               "left": win32api.GetSystemMetrics(0)//2 - 50, 
               "width": 100, "height": 100}

    print("--- [ Continuous Stability Active ] ---")
    win32api.Beep(1000, 200)

    last_pull = 0

    while True:
        if keyboard.is_pressed('f3') and not is_active:
            is_active = True
            win32api.Beep(1200, 100)
        if keyboard.is_pressed('f4') and is_active:
            is_active = False
            win32api.Beep(400, 200)

        # التحقق من الضغط المستمر على الماوس
        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            if 'prev_gray' in locals():
                # خوارزمية محسنة لكشف الإزاحة حتى لو كانت بسيطة
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                # إذا وجد حركة أو "استمر" في حالة السحب
                if M["m00"] > MIN_DETECTION:
                    target_y = (M["m01"] / M["m00"] - 50)
                    
                    # معادلة تمنع انقطاع السحب المفاجئ
                    pull = target_y * SENSITIVITY
                    current_pull = last_pull + (pull - last_pull) * SMOOTHING
                    
                    # تنفيذ السحب
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(current_pull), 0, 0)
                    last_pull = current_pull
                else:
                    # في حال فقد التتبع للحظة، يستمر في سحب بسيط لمنع القفز للأعلى
                    if last_pull > 1:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(last_pull * 0.5), 0, 0)
                        last_pull *= 0.8 # تصفير تدريجي بدلاً من الانقطاع المفاجئ
            
            prev_gray = gray
        else:
            last_pull = 0
            if 'prev_gray' in locals(): del prev_gray
            time.sleep(0.01)

        time.sleep(0.001)

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        run_stable_system()
