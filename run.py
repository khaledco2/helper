import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
from mss import mss

# --- إعدادات الرؤية الجديدة ---
SENSITIVITY = 1.6       # قوة سحب موزونة
is_active = False

def run_edge_logic():
    global is_active
    sct = mss()
    monitor = {"top": win32api.GetSystemMetrics(1)//2 - 40, 
               "left": win32api.GetSystemMetrics(0)//2 - 40, 
               "width": 80, "height": 80}

    print("--- [ Edge Detection Mode - Works on Walls ] ---")
    win32api.Beep(1000, 200)

    while True:
        if keyboard.is_pressed('f3'): is_active = True
        if keyboard.is_pressed('f4'): is_active = False

        if is_active and win32api.GetAsyncKeyState(0x01) < 0:
            img = np.array(sct.grab(monitor))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            
            # --- السر هنا: تحويل الصورة لخطوط بيضاء وسوداء (الحواف فقط) ---
            edges = cv2.Canny(gray, 100, 200) 
            
            if 'prev_edges' in locals():
                diff = cv2.absdiff(prev_edges, edges)
                M = cv2.moments(diff)
                
                if M["m00"] > 50:
                    pull = (M["m01"] / M["m00"] - 40) * SENSITIVITY
                    if abs(pull) > 0.5:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(pull), 0, 0)
            
            prev_edges = edges
        else:
            if 'prev_edges' in locals(): del prev_edges
            time.sleep(0.01)

        time.sleep(0.005)

if __name__ == "__main__":
    run_edge_logic()
