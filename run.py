# 1. تعريف واجهة التحكم في الماوس (Win32 API) كما في الملفات الاحترافية
$signature = @"
[DllImport("user32.dll")]
public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
[DllImport("user32.dll")]
public static extern short GetAsyncKeyState(int vKey);
"@
$API = Add-Type -MemberDefinition $signature -Name "Win32Internal" -Namespace Win32 -PassThru

# 2. إعدادات قيم الريكويل (نفس منطق الملف .T المستخرج)
$PullDownAmount = 4   # مقدار السحب للأسفل (بكسل)
$HorizontalShaky = 0  # التعديل الأفقي (اختياري)
$DelayMs = 15         # سرعة التكرار (ميلي ثانية)
$LeftMouseButton = 0x01 # كود تتبع زر الماوس الأيسر

Write-Host "--- آلية التتبع والعمل العكسي نشطة ---" -ForegroundColor Cyan
Write-Host "اضغط واستمر بضغط زر الماوس الأيسر للتفعيل" -ForegroundColor Yellow
Write-Host "اضغط CTRL+C لإيقاف السكربت نهائياً" -ForegroundColor Red

# 3. حلقة التتبع اللحظي (The Core Loop)
try {
    while($true) {
        # التحقق من حالة الزر الأيسر (GetAsyncKeyState)
        # هذه هي نفس الطريقة التي يستخدمها ملف 18902677491.T للتتبع 
        $isPressed = $API::GetAsyncKeyState($LeftMouseButton)
        
        if ($isPressed -lt 0) {
            # تنفيذ "العمل العكسي": تحريك الماوس للأسفل (MOUSEEVENTF_MOVE = 0x0001)
            $API::mouse_event(0x0001, 0, $PullDownAmount, 0, 0)
            
            # تأخير بسيط لمحاكاة سرعة إطلاق النار في اللعبة
            Start-Sleep -Milliseconds $DelayMs
        } else {
            # تقليل استهلاك المعالج عند عدم الضغط
            Start-Sleep -Milliseconds 5
        }
    }
} catch {
    Write-Host "`nتم إيقاف آلية العمل." -ForegroundColor Gray
}
