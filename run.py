import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import ctypes
from PIL import ImageGrab

# --- إعدادات الذكاء الفائق ---
SENSITIVITY_RATIO = 2.5  # معامل القوة (يمكنك تعديله حسب تجربتك)
is_active = False

def play_sound(mode):
    if mode == "on":
        win32api.Beep(800, 150)
        win32api.Beep(1200, 150)
    elif mode == "off":
        win32api.Beep(400, 300)
    elif mode == "startup":
        win32api.Beep(1000, 100)
        win32api.Beep(1000, 100)

def get_recoil_amount(prev, curr):
    diff = cv2.absdiff(prev, curr)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    moments = cv2.moments(thresh)
    if moments["m00"] > 50:
        dy = moments["m01"] / moments["m00"] - (thresh.shape[0] / 2)
        return dy
    return 0

def run_smart_system():
    global is_active
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    ROI = (w//2 - 60, h//2 - 60, w//2 + 60, h//2 + 60)
    
    print("="*40)
    print(" [✔] AI Dynamic System - ACTIVE")
    print(" [✔] F3: ON (Beep Up) | F4: OFF (Beep Down)")
    print("="*40)
    
    play_sound("startup") # صوت عند بداية تشغيل السكربت

    prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))

    while True:
        # التحكم بالصوت والتشغيل
        if keyboard.is_pressed('f3') and not is_active:
            is_active = True
            play_sound("on")
            print(">>> System: ON")
        
        if keyboard.is_pressed('f4') and is_active:
            is_active = False
            play_sound("off")
            print(">>> System: OFF")

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            curr_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
            recoil_gap = get_recoil_amount(prev_frame, curr_frame)
            
            if recoil_gap > 0.5:
                # الحساب الذكي لمقدار الارتداد الفعلي
                pull_force = int(recoil_gap * SENSITIVITY_RATIO)
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, pull_force, 0, 0)
            
            prev_frame = curr_frame
        else:
            if time.time() % 0.1 < 0.01:
                prev_frame = np.array(ImageGrab.grab(bbox=ROI).convert('L'))
        
        time.sleep(0.005)

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        run_smart_system()
    else:
        print("يرجى تشغيل البور شيل كمسؤول!")
        time.sleep(5)
