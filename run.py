import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from mss import mss # مكتبة التصوير الفائق

# --- إعدادات النعومة القصوى ---
SENSITIVITY = 2.4 
SMOOTHING_FACTOR = 0.5 # كلما قل الرقم زادت النعومة (0.1 - 0.9)
is_active = False

def play_sound(freq, duration):
    win32api.Beep(freq, duration)

def run_ultra_smooth():
    global is_active
    sct = mss() # تهيئة المصور السريع
    
    # تحديد منطقة الفحص (صغيرة جداً لسرعة البرق)
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 40, 
               "left": win32api.GetSystemMetrics(0)//2 - 40, 
               "width": 80, "height": 80}

    print("--- [ Ultra-Smooth System Active ] ---")
    play_sound(1000, 200)

    # ذاكرة الحركة للتنعيم
    last_pull = 0

    while True:
        if keyboard.is_pressed('f3') and not is_active:
            is_active = True
            play_sound(1200, 100)
        if keyboard.is_pressed('f4') and is_active:
            is_active = False
            play_sound(400, 200)

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط الشاشة بسرعة البرق
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            if 'prev_gray' in locals():
                # حساب الإزاحة
                diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                M = cv2.moments(thresh)
                
                if M["m00"] > 40:
                    target_pull = (M["m01"] / M["m00"] - 40) * SENSITIVITY
                    
                    # --- خوارزمية التنعيم (Smoothing Algorithm) ---
                    # بدلاً من القفز، نتحرك بجزء من المسافة المطلوبة فقط
                    current_pull = last_pull + (target_pull - last_pull) * SMOOTHING_FACTOR
                    
                    if abs(current_pull) > 0.5:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(current_pull), 0, 0)
                        last_pull = current_pull
                else:
                    last_pull = 0 # تصفير الحركة عند التوقف
            
            prev_gray = gray
        else:
            last_pull = 0
            if 'prev_gray' in locals(): del prev_gray # تنظيف الذاكرة
            time.sleep(0.01)

        time.sleep(0.001) # استجابة 1ms

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        run_ultra_smooth()
