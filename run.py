import win32api, win32con, win32gui, ctypes, threading, time, pydirectinput
from multiprocessing.connection import Listener
from random import uniform

# --- إعدادات الأداء الفائقة ---
pydirectinput.PAUSE = 0
ctypes.windll.user32.SetProcessDPIAware()

# المتغيرات المشتركة بين نظام الرسم ونظام السحب
class GlobalState:
    rcs_active = False
    current_weapon = "None"
    recoil_val = 0
    active_slot = 1
    overlay_visible = True
    running = True

state = GlobalState()

# 1️⃣ تحسين فلترة الهدف وتجنب صفر الحركة (Logic)
def apply_recoil_hardware(val):
    if state.rcs_active and val > 0:
        # إضافة عشوائية بشرية (Humanization) لفلترة التتبع
        jitter = uniform(-1.2, 1.2)
        final_y = int(round(val + jitter))
        
        # 2️⃣ تصحيح اتجاه Y عبر محاكي الهاردوير
        if final_y > 1: # تجنب صفر الحركة
            pydirectinput.moveRel(0, final_y, relative=True)

# 3️⃣ توسيع منطقة الرصد (نظام الـ Listener المحدث)
def socket_server():
    address = ('localhost', 1337)
    serv = Listener(address)
    while state.running:
        try:
            client = serv.accept()
            while True:
                msg = client.recv() # استقبال البيانات من السكربت الأساسي
                # [تحديث الحالة هنا بناءً على الرسالة القادمة]
                # مثال بسيط لتحديث الحالة
                state.rcs_active = True if "True" in msg else False
        except:
            break

# 4️⃣ نظام الرسم المحسن (Overlay)
def draw_overlay():
    hInstance = win32api.GetModuleHandle()
    className = 'SiedlerLP_Overlay'
    
    # تعريف النافذة الشفافة
    wndClass = win32gui.WNDCLASS()
    wndClass.lpfnWndProc = {win32con.WM_PAINT: on_paint}
    wndClass.lpszClassName = className
    wndClassAtom = win32gui.RegisterClass(wndClass)
    
    exStyle = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
    style = win32con.WS_POPUP
    
    hwnd = win32gui.CreateWindowEx(
        exStyle, wndClassAtom, "Overlay", style,
        0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1),
        0, 0, hInstance, None
    )
    
    win32gui.SetLayeredWindowAttributes(hwnd, 0x00ffffff, 255, win32con.LWA_COLORKEY)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    
    while state.running:
        win32gui.RedrawWindow(hwnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW)
        time.sleep(0.1) # توفير موارد الـ CPU

def on_paint(hwnd, msg, wp, lp):
    hdc, ps = win32gui.BeginPaint(hwnd)
    if state.overlay_visible:
        # رسم مستطيل المعلومات (كما في كودك)
        win32gui.SetTextColor(hdc, win32api.RGB(0, 255, 0) if state.rcs_active else win32api.RGB(255, 0, 0))
        win32gui.DrawText(hdc, f"RCS: {'ACTIVE' if state.rcs_active else 'OFF'}", -1, (10, 10, 200, 50), win32con.DT_LEFT)
    win32gui.EndPaint(hwnd, ps)

# --- تشغيل المحرك ---
if __name__ == "__main__":
    # تشغيل الخادم والرسام في خيوط منفصلة
    threading.Thread(target=socket_server, daemon=True).start()
    threading.Thread(target=draw_overlay, daemon=True).start()
    
    print("System Online. Use '0' to toggle.")
    
    while True:
        # فحص ضغط الماوس في الحلقة الرئيسية لضمان أقل تأخير (Zero Latency)
        if win32api.GetAsyncKeyState(0x01) & 0x8000 and state.rcs_active:
            apply_recoil_hardware(13) # مثال قيمة الارتداد
            time.sleep(0.09) # متوافق مع سرعة السلاح
        time.sleep(0.001)
