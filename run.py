# تعريف دوال النظام للتحكم في الماوس (Win32 API)
$signature = @"
[DllImport("user32.dll")]
public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
[DllImport("user32.dll")]
public static extern short GetAsyncKeyState(int vKey);
"@
$API = Add-Type -MemberDefinition $signature -Name "Win32MouseControl" -Namespace Win32 -PassThru

# إعدادات الريكويل (تستطيع تعديلها من جيت هاب مباشرة)
$PullDownAmount = 5  # قوة السحب لأسفل
$Delay = 20          # السرعة (ميلي ثانية)

Write-Host "--- التتبع نشط من GitHub (نسخة PowerShell) ---" -ForegroundColor Green

try {
    while($true) {
        # التتبع: التحقق من ضغط زر الماوس الأيسر (0x01)
        if ($API::GetAsyncKeyState(0x01) -lt 0) {
            # العمل العكسي: سحب الماوس لأسفل
            $API::mouse_event(0x0001, 0, $PullDownAmount, 0, 0)
            Start-Sleep -Milliseconds $Delay
        }
        Start-Sleep -Milliseconds 5
    }
} catch {
    Write-Host "تم إيقاف السكربت."
}
