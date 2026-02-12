import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- إعدادات الاحتراف (المنطقة الذهبية) ---
BASE_SENS = 0.32       # القوة الأساسية (متوازنة جداً)
SMOOTHING = 0.15       # نعومة حريرية لمنع الارتجاف
STABILIZER = 1.2       # قوة إضافية عند اكتشاف هروب السلاح للأعلى
is_active = False

def run_perfect_system():
    global is_active
    sct = mss()
    
    # منطقة رؤية محسنة لا تخطئ الهدف
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 40, 
               "left": win32api.GetSystemMetrics(0)//2 - 40, 
               "width": 80, "height": 80}

    print("--- [ Golden Edition: Stable & Smooth ] ---")
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
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            if 'prev_gray' in locals():
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, 35, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                if M["m00"] > 50:
                    # حساب المسافة التي قطعها السلاح للأعلى
                    dist_y = (M["m01"] / M["m00"] - 40)
                    
                    # إذا كان السلاح يصعد بقوة، نزيد القوة تلقائياً
                    current_sens = BASE_SENS
                    if dist_y > 5: current_sens *= STABILIZER
                    
                    target_pull = dist_y * current_sens
                    
                    # تنعيم الحركة (السر في النعومة)
                    final_move = last_pull + (target_pull - last_pull) * SMOOTHING
                    
                    if abs(final_move) > 0.1:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(final_move), 0, 0)
                        last_pull = final_move
                else:
                    last_pull = 0
            
            prev_gray = gray
        else:
            last_pull = 0
            time.sleep(0.01)

        time.sleep(0.001) # استجابة فائقة السرعة

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        run_perfect_system()
