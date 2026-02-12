import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from PIL import ImageGrab

# --- إعدادات القوة والاستجابة ---
SENSITIVITY = 3.8   # رفعنا الحساسية لضمان "التمسك" بالهدف
ACCURACY = 1.0     # عتبة الحركة (كلما قل زاد التحسس)
is_running = False

def start_engine():
    global is_running
    
    # تحديد مركز الشاشة تلقائياً
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    mid_x, mid_y = w // 2, h // 2
    # منطقة مسح صغيرة جداً (50x50) لزيادة السرعة القصوى ومنع التعليق
    ROI = (mid_x - 25, mid_y - 25, mid_x + 25, mid_y + 25)
    
    print(f"[✔] نظام التتبع المستمر نشط | الدقة: {w}x{h}")
    
    # تحضير الإطار الأول
    prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))

    while True:
        # أزرار التحكم
        if keyboard.is_pressed('f3'): is_running = True
        if keyboard.is_pressed('f4'): is_running = False

        if is_running and win32api.GetAsyncKeyState(0x01) < 0:
            # التقاط سريع جداً
            curr_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
            
            # حساب الفرق بين الصورتين (المسؤول عن الثبات)
            diff = cv2.absdiff(prev_frame, curr_frame)
            _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
            
            # حساب مركز الثقل للحركة (للتأكد من اتجاه الارتداد)
            M = cv2.moments(thresh)
            if M["m00"] > 100: # إذا وجد حركة حقيقية
                # سحب مستمر وليس لحظي
                pull = int(SENSITIVITY * 8)
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, pull, 0, 0)
            
            # أهم خطوة: تحديث الإطار فوراً لضمان عدم "الافلات" في الطلقة التالية
            prev_frame = curr_frame
            time.sleep(0.001) # تزامن فائق السرعة
        else:
            # إعادة التقاط الإطار المرجعي عند التوقف عن الإطلاق
            if time.time() % 0.1 < 0.01:
                prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
        
        time.sleep(0.001)

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        start_engine()
    else:
        print("يرجى التشغيل كمسؤول!")
        time.sleep(5)
