# استدعاء الدوال المتقدمة للتحكم في الماوس من نظام ويندوز
$signature = @"
[DllImport("user32.dll")]
public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
[DllImport("user32.dll")]
public static extern short GetAsyncKeyState(int vKey);
"@
$API = Add-Type -MemberDefinition $signature -Name "SystemController" -Namespace Win32 -PassThru

# إعدادات متقدمة (نفس آلية الملفات المرسلة)
$BasePullDown = 4    # القوة الأساسية للسحب
$RandomFactor = 2    # عامل التغيير العشوائي (للتخفي)
$Delay = 15          # سرعة الاستجابة

Write-Host "--- Script Loaded: Advanced Reverse Mechanism ---" -ForegroundColor Cyan
Write-Host "Monitoring Hardware Input..." -ForegroundColor Gray

try {
    while($true) {
        # التتبع: فحص ضغط زر الماوس الأيسر (0x01)
        if ($API::GetAsyncKeyState(0x01) -lt 0) {
            
            # العمل العكسي المتغير (يحاكي حركة اليد البشرية)
            $FinalMove = $BasePullDown + (Get-Random -Minimum 0 -Maximum $RandomFactor)
            
            # تنفيذ الحركة العكسية (Relative Move)
            $API::mouse_event(0x0001, 0, $FinalMove, 0, 0)
            
            Start-Sleep -Milliseconds $Delay
        }
        Start-Sleep -Milliseconds 5
    }
} catch {
    Write-Host "Disconnected."
}
