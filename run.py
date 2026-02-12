import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from PIL import ImageGrab
import threading

# --- إعدادات القوة والاستجابة ---
SENSITIVITY = 4.5   # زيادة الحساسية
ACCURACY = 0.4      # تقليل العتبة
SMOOTHING = 0.1    # إضافة تنعيم
PULL_DOWN_RATIO = 0.8 # نسبة السحب للأسفل
PULL_LEFT_RIGHT_RATIO = 0.1 # نسبة السحب الجانبي

# --- متغيرات عالمية ---
is_running = False
prev_frame = None
mouse_x, mouse_y = 0, 0 # موقع الفأرة الحالي

def calculate_pull(dx, dy):
    """
    حساب مقدار السحب المطلوب للتعويض عن الارتداد.
    """
    pull_y = int(SENSITIVITY * PULL_DOWN_RATIO * dy)
    pull_x = int(SENSITIVITY * PULL_LEFT_RIGHT_RATIO * dx)
    return pull_x, pull_y

def move_mouse(x, y):
    """
    تحريك الفأرة بسلاسة باستخدام التنعيم.
    """
    global mouse_x, mouse_y
    mouse_x += x * SMOOTHING
    mouse_y += y * SMOOTHING
    
    # تقريب القيم إلى أقرب عدد صحيح
    target_x = int(mouse_x)
    target_y = int(mouse_y)
    
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, target_x - win32api.GetCursorPos()[0], target_y - win32api.GetCursorPos()[1], 0, 0)
    win32api.SetCursorPos((target_x, target_y)) # تحديث الموقع الفعلي
    

def detection_loop(ROI):
    """
    حلقة الكشف عن الحركة وتحريك الماوس.
    """
    global is_running, prev_frame, mouse_x, mouse_y
    
    # تهيئة الإطار الأول
    prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    mouse_x, mouse_y = w // 2, h // 2 # تهيئة موقع الفأرة
    win32api.SetCursorPos((mouse_x, mouse_y)) # ضبط موقع الفأرة
    
    while is_running:
        if win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط سريع جداً
            curr_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
            
            # حساب الفرق بين الصورتين (المسؤول عن الثبات)
            diff = cv2.absdiff(prev_frame, curr_frame)
            _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
            
            # حساب مركز الثقل للحركة (للتأكد من اتجاه الارتداد)
            M = cv2.moments(thresh)
            if M["m00"] > 100: # إذا وجد حركة حقيقية
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # حساب مقدار السحب المطلوب
                dx = cX - 25  # المسافة من مركز ROI
                dy = cY - 25
                pull_x, pull_y = calculate_pull(dx, dy)
                
                # تحريك الماوس بسلاسة
                move_mouse(pull_x, pull_y)
            
            # أهم خطوة: تحديث الإطار فوراً لضمان عدم "الافلات" في الطلقة التالية
            prev_frame = curr_frame
            time.sleep(0.001) # تزامن فائق السرعة
        else:
            # إعادة التقاط الإطار المرجعي عند التوقف عن الإطلاق
            if time.time() % 0.1 < 0.01:
                prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
        
        time.sleep(0.001)

def start_engine():
    global is_running

    # تحديد مركز الشاشة تلقائياً
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    mid_x, mid_y = w // 2, h // 2
    # منطقة مسح صغيرة جداً (50x50) لزيادة السرعة القصوى ومنع التعليق
    ROI = (mid_x - 25, mid_y - 25, mid_x + 25, mid_y + 25)

    print(f"[✔] نظام التتبع المستمر نشط | الدقة: {w}x{h}")

    # إنشاء مؤشر للكشف عن الحركة
    detection_thread = threading.Thread(target=detection_loop, args=(ROI,))
    detection_thread.daemon = True # إنهاء المؤشر عند إغلاق البرنامج
    detection_thread.start()

    while True:
        # أزرار التحكم
        if keyboard.is_pressed('f3'):
            is_running = True
            print("[✔] بدأ نظام التثبيت")
        if keyboard.is_pressed('f4'):
            is_running = False
            print("[!] توقف نظام التثبيت")

        time.sleep(0.1)

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        start_engine()
    else:
        print("يرجى التشغيل كمسؤول!")
        time.sleep(5)
