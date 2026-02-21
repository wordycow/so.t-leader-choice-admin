@echo off
setlocal
set BASE=C:\leemay_project
set LOGDIR=%BASE%\logs
set STUB=%BASE%\ai_trading_5000_stub.py

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo.
echo ============================================
echo  START 5000 (SAFE STUB)
echo ============================================
echo.

REM 1) 5000 LISTENING PID kill
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
  echo [KILL] PID=%%a on :5000
  taskkill /PID %%a /F >nul 2>nul
)

REM 2) python 확인
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found in PATH
  echo [ERROR] Python not found in PATH>>"%LOGDIR%\ai_trading_5000_stderr.log"
  exit /b 1
)

REM 3) stub 파일 확인
if not exist "%STUB%" (
  echo [ERROR] Missing: %STUB%
  echo [ERROR] Missing stub: %STUB%>>"%LOGDIR%\ai_trading_5000_stderr.log"
  exit /b 1
)

REM 4) 인코딩 안전장치
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM 5) 실행 (풀경로 강제)
echo [RUN] python -u "%STUB%"
start "AI_TRADING_5000_STUB" /min cmd /c ^
"cd /d %BASE% && python -u "%STUB%" >> %LOGDIR%\ai_trading_5000_stdout.log 2>> %LOGDIR%\ai_trading_5000_stderr.log"

echo [OK] started 5000 stub
endlocal
exit /b 0