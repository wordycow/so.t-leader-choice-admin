@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM ============================================================
REM LeeMay - Start AI Trading Bot (Port 5000)
REM FIX: Avoid PowerShell Start-Process python (alias issue)
REM      Launch via CMD runner with stdout/err to logs
REM ============================================================

set "BASE=C:\leemay_project"
cd /d "%BASE%"

if not exist "logs" mkdir "logs"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss_fff"') do set "TS=%%i"
set "RID=%RANDOM%"

set "BOT_FILE=%BASE%\upbit-smart-bot-v8.0-ULTIMATE.py"
set "OUT_LOG=%BASE%\logs\ai_trading_5000_%TS%_%RID%.out.log"
set "ERR_LOG=%BASE%\logs\ai_trading_5000_%TS%_%RID%.err.log"
set "RUNNER=%BASE%\logs\run_5000_%TS%_%RID%.cmd"

if not exist "%BOT_FILE%" (
  echo [FAIL] Bot file not found: %BOT_FILE%
  exit /b 1
)

REM 이미 5000이 열려 있으면 종료
powershell -NoProfile -Command "$c=Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue; if($c){exit 0}else{exit 1}" >nul 2>&1
if %errorlevel%==0 (
  echo [OK] Port 5000 already listening.
  exit /b 0
)

REM env
set "PYTHONPATH=%BASE%;%BASE%\_py_tree\upbit-bot-v8-ultimate-release;%PYTHONPATH%"
set "PORT=5000"
set "FLASK_RUN_PORT=5000"
set "PYTHONUNBUFFERED=1"

echo [INFO] Starting bot via CMD runner...
echo   BOT = %BOT_FILE%
echo   OUT = %OUT_LOG%
echo   ERR = %ERR_LOG%
echo   RUN = %RUNNER%
echo.

REM runner 생성 (여기 안에서는 따옴표/리다이렉트가 안전함)
(
  echo @echo off
  echo chcp 65001 ^>nul
  echo cd /d "%BASE%"
  echo echo ==== START %%date%% %%time%% ==== ^> "%OUT_LOG%"
  echo echo PYTHONPATH=%%PYTHONPATH%% ^>^> "%OUT_LOG%"
  echo echo PORT=%%PORT%% ^>^> "%OUT_LOG%"
  echo echo FLASK_RUN_PORT=%%FLASK_RUN_PORT%% ^>^> "%OUT_LOG%"
  echo echo. ^>^> "%OUT_LOG%"
  echo echo ==== STDERR ==== ^> "%ERR_LOG%"
  echo where python ^>^> "%OUT_LOG%" 2^>^> "%ERR_LOG%"
  echo python --version ^>^> "%OUT_LOG%" 2^>^> "%ERR_LOG%"
  echo echo. ^>^> "%OUT_LOG%"
  echo python -u "%BOT_FILE%" ^>^> "%OUT_LOG%" 2^>^> "%ERR_LOG%"
  echo echo EXITCODE=%%errorlevel%% ^>^> "%ERR_LOG%"
) > "%RUNNER%"

REM 최소화 실행 (창 유지 필요하면 /min 빼고 실행해도 됨)
start "" /min "%RUNNER%"

REM 30초 폴링으로 5000 확인
powershell -NoProfile -Command ^
"$ok=$false; for($i=0;$i -lt 60;$i++){ $c=Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue; if($c){$ok=$true; break}; Start-Sleep -Milliseconds 500 }; if($ok){'OK: Port 5000 LISTEN'} else {'FAIL: Port 5000 NOT listening'}"

echo [DONE]
exit /b 0