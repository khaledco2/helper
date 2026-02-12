import cv2
import numpy as np
import time
import win32api, win32con, keyboard, ctypes
import threading
import mss

# --- الإعدادات ---
SENSITIVITY = 0.5   # تعديل الحساسية لتناسب ميكانيكا الألعاب
SMOOTHING = 0.2     # تنعيم الحركة (كلما قل زاد البطء والسلاسة)
MONITOR_SIZE = 50   # مساحة المسح 50x50

is_running = False

def move_mouse_relative(dx, dy):
    """ تحريك الفأرة بشكل نسبي سلس ليتوافق مع محركات الألعاب """
    if dx != 0 or dy != 0:
        # حساب الحركة المنعمة
        move_x = int(dx * SENSITIVITY)
        move_y = int(dy * SENSITIVITY)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

def detection_loop():
    global is_running
    sct = mss.mss()
    
    # تحديد منطقة المسح في منتصف الشاشة
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    region = {
        'top': (h // 2) - (MONITOR_SIZE // 2),
        'left': (w // 2) - (MONITOR_SIZE // 2),
        'width': MONITOR_SIZE,
        'height': MONITOR_SIZE
    }

    # الإطار الأول
    last_img = np.array(sct.grab(region))
    last_gray = cv2.cvtColor(last_img, cv2.COLOR_BGRA2GRAY)

    while True:
        if is_running and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط سريع
            curr_img = np.array(sct.grab(region))
            curr_gray = cv2.cvtColor(curr_img, cv2.COLOR_BGRA2GRAY)
            
            # فرق الحركة
            diff = cv2.absdiff(last_gray, curr_gray)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            M = cv2.moments(thresh)
            if M["m00"] > 100:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # المسافة عن المركز (25 هو منتصف الـ 50)
                dx = cX - (MONITOR_SIZE // 2)
                dy = cY - (MONITOR_SIZE // 2)
                
                move_mouse_relative(dx, dy)
            
            last_gray = curr_gray
        else:
            time.sleep(0.01) # تقليل استهلاك المعالج عند عدم الإطلاق

def start_engine():
    global is_running
    print("[✔] المحرك جاهز | F3 للتشغيل | F4 للإيقاف")
    
    threading.Thread(target=detection_loop, daemon=True).start()

    while True:
        if keyboard.is_pressed('f3'):
            is_running = True
            print("RUNNING")
        if keyboard.is_pressed('f4'):
            is_running = False
            print("STOPPED")
        time.sleep(0.1)

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        start_engine()
    else:
        print("أعد التشغيل كمسؤول!")
