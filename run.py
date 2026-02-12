import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss

# --- قيم منخفضة جداً لإنهاء "الجنون" ---
SENSITIVITY = 0.08     # تقليل ضخم جداً (كان 0.45) لمنع الماوس من الهروب للأرض
SMOOTHING = 0.05       # تنعيم فائق لجعله بطيء جداً وانسيابي
is_active = False

def run_final_fix():
    global is_active
    sct = mss()
    
    # منطقة مسح صغيرة جداً لتقليل الأخطاء
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 25, 
               "left": win32api.GetSystemMetrics(0)//2 - 25, 
               "width": 50, "height": 50}

    print("--- [ Anti-Craziness Fix Active ] ---")
    win32api.Beep(800, 200)

    last_pull = 0

    while True:
        if keyboard.is_pressed('f3') and not is_active:
            is_active = True
            win32api.Beep(1000, 100)
        if keyboard.is_pressed('f4') and is_active:
            is_active = False
            win32api.Beep(400, 200)

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            if 'prev_gray' in locals():
                diff = cv2.absdiff(prev_gray, gray)
                # رفع العتبة ليتجاهل كل شيء ما عدا الحركة القوية
                _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                if M["m00"] > 100: # زيادة شرط كمية الحركة لبدء السحب
                    target_y = (M["m01"] / M["m00"] - 25)
                    
                    # السحب الآن أضعف بـ 10 مرات من النسخة السابقة
                    pull = target_y * SENSITIVITY
                    current_pull = last_pull + (pull - last_pull) * SMOOTHING
                    
                    if abs(current_pull) > 0.1:
                        # تحريك ناعم جداً (بكسل بكسل)
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(current_pull), 0, 0)
                        last_pull = current_pull
            
            prev_gray = gray
        else:
            last_pull = 0
            time.sleep(0.02) # زيادة وقت الراحة لتقليل سرعة السحب

        time.sleep(0.005) # إبطاء السكربت عمداً ليتناسب مع سرعة يد الإنسان

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        run_final_fix()
