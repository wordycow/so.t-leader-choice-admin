@echo off
REM ============================================================
REM Lee May Control Center - BOTS STOP
REM ============================================================
REM 목적: 봇만 종료, CONTROL(5001, cloudflared)은 유지
REM - AI Trading Bot (포트 5000)
REM - YouTube Learner
REM - 기타 학습 봇들
REM ============================================================

echo.
echo ========================================
echo Lee May Control Center - BOTS STOP
echo ========================================
echo.

REM ============================================================
REM 1. AI Trading Bot 종료 확인
REM ============================================================
echo [1/2] AI Trading Bot 종료 확인 중...
echo.

REM upbit-smart-bot 프로세스 찾기
tasklist /FI "WINDOWTITLE eq upbit-smart-bot*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [ACTION] AI Trading Bot 종료 중...
    taskkill /FI "WINDOWTITLE eq upbit-smart-bot*" /F >NUL 2>&1
    timeout /t 2 /nobreak >NUL
    echo [OK] AI Trading Bot 종료 완료
) else (
    echo [INFO] AI Trading Bot 실행 중이 아님
)
echo.

REM ============================================================
REM 2. 학습 봇 종료 확인
REM ============================================================
echo [2/2] 학습 봇 종료 확인 중...
echo.

REM youtube_learner 프로세스 찾기
tasklist /FI "WINDOWTITLE eq youtube*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [ACTION] YouTube Learner 종료 중...
    taskkill /FI "WINDOWTITLE eq youtube*" /F >NUL 2>&1
    timeout /t 2 /nobreak >NUL
    echo [OK] YouTube Learner 종료 완료
) else (
    echo [INFO] YouTube Learner 실행 중이 아님
)
echo.

REM ============================================================
REM CONTROL 서비스 유지 확인
REM ============================================================
echo ========================================
echo CONTROL 서비스 상태 확인
echo ========================================
echo.

echo [CHECK] API Server (5001)...
tasklist /FI "WINDOWTITLE eq api_server*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [OK] API Server 실행 중 (유지됨)
) else (
    echo [WARN] API Server 실행 중이 아님 - 01_CONTROL_START.bat 실행 필요
)
echo.

echo [CHECK] Cloudflare Tunnel...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I "cloudflared.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [OK] Cloudflare Tunnel 실행 중 (유지됨)
) else (
    echo [WARN] Cloudflare Tunnel 실행 중이 아님 - 01_CONTROL_START.bat 실행 필요
)
echo.

REM ============================================================
REM 완료
REM ============================================================
echo ========================================
echo BOTS STOP 완료
echo ========================================
echo.
echo 종료된 봇: Trading Bot, Learning Bots
echo 유지된 서비스: API Server (5001), Cloudflare Tunnel
echo.

pause
