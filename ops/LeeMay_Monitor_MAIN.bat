@echo off
setlocal
chcp 65001 >nul

set "BASE=C:\leemay_project"
set "ADMIN_KEY=1106"

title LeeMay MONITOR (Ports/Health/Logs)

:LOOP
cls
echo ============================================================
echo  LeeMay MONITOR    %date% %time%
echo  BASE: %BASE%
echo ============================================================
echo.

echo --- PORTS (LISTEN) ---
powershell -NoProfile -Command ^
  "$ports=@(5001,5000,11434); foreach($pt in $ports){ $c=Get-NetTCPConnection -LocalPort $pt -State Listen -ErrorAction SilentlyContinue; if($c){ $p=($c.OwningProcess|Sort-Object -Unique)-join ','; Write-Host ('PORT '+$pt+': ON  PID='+$p) } else { Write-Host ('PORT '+$pt+': OFF') } }"
echo.

echo --- HEALTH (5001) ---
curl -m 2 http://127.0.0.1:5001/health 2>nul
echo.
echo --- OPS STATUS (5001) ---
curl -m 2 http://127.0.0.1:5001/api/ops/status -H "X-Admin-Key: %ADMIN_KEY%" 2>nul
echo.

echo --- TAIL ops_api.log (last 12) ---
powershell -NoProfile -Command "Get-Content -Path 'C:\leemay_project\logs\ops_api.log' -Tail 12 -ErrorAction SilentlyContinue"
echo.

echo --- TAIL bots_start_last.log (last 12) ---
powershell -NoProfile -Command "Get-Content -Path 'C:\leemay_project\logs\bots_start_last.log' -Tail 12 -ErrorAction SilentlyContinue"
echo.

echo --- LATEST ai_trading_5000_*.log (last 30) ---
powershell -NoProfile -Command ^
  "$f=Get-ChildItem 'C:\leemay_project\logs\ai_trading_5000_*.log' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1; if($f){ Write-Host ('LATEST='+$f.FullName); Get-Content $f.FullName -Tail 30 } else { Write-Host 'NO ai_trading log yet' }"
echo.

echo [R] Refresh now   [Q] Quit   (auto refresh in 3 sec)
choice /c RQ /n /t 3 /d R >nul
if errorlevel 2 exit /b
goto LOOP