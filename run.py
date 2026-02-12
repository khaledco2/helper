import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from PIL import ImageGrab

# --- الإعدادات الأساسية ---
SENSITIVITY = 1.6   # قوة رد الفعل (ارفعها إذا كان السلاح لا يزال يرتفع)
is_running = False  # الحالة الافتراضية

def check_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

def start_engine():
    global is_running
    
    # منطقة الفحص (مركز الشاشة 100x100 بكسل)
    # هذه المنطقة هي التي يراقب فيها السكربت حركة البكسلات
    ROI = (910, 490, 1010, 590) 
    
    print("="*45)
    print(" [✔] نظام التتبع الديناميكي يعمل بنجاح")
    print(" [!] F3: تفعيل (ON) | F4: إيقاف مؤقت (OFF)")
    print(" [!] النظام يراقب الارتداد الآن ويعاكسه لحظياً")
    print("="*45)

    # التقاط أول إطار للمقارنة
    prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))

    while True:
        # التحكم في التشغيل
        if keyboard.is_pressed('f3') and not is_running:
            is_running = True
            print("[ON] >>> SYSTEM ACTIVE")
            win32api.Beep(1000, 200)
        
        if keyboard.is_pressed('f4') and is_running:
            is_running = False
            print("[OFF] >>> SYSTEM PAUSED")
            win32api.Beep(500, 400)

        if is_running:
            # التحقق من ضغط زر الفأرة الأيسر (0x01)
            if win32api.GetAsyncKeyState(0x01) < 0:
                # التقاط الإطار الحالي
                curr_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
                
                # حساب الإزاحة بين الإطارين (Optical Flow)
                # هذه الخوارزمية تكتشف أين تحركت البكسلات
                flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                
                # متوسط الحركة على المحور العمودي (Y)
                movement_y = np.mean(flow[..., 1])
                
                # إذا تحركت الشاشة للأعلى (ارتداد)
                if movement_y < -0.05:
                    # حساب مقدار السحب العكسي
                    pull_amount = int(abs(movement_y) * SENSITIVITY * 12)
                    # تنفيذ السحب فوراً
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, pull_amount, 0, 0)
                
                prev_frame = curr_frame
            else:
                # تحديث الإطار السابق أثناء عدم الإطلاق لضمان سلاسة المقارنة
                prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
        
        time.sleep(0.007) # سرعة معالجة عالية جداً لتجنب التأخير (Lag)

if __name__ == "__main__":
    if check_admin():
        try:
            start_engine()
        except Exception as e:
            print(f"حدث خطأ غير متوقع: {e}")
            time.sleep(5)
    else:
        print("خطأ: يجب تشغيل PowerShell أو CMD كمسؤول!")
        time.sleep(5)
