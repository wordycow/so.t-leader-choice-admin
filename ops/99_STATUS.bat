@echo off
REM ============================================================
REM Lee May Control Center - STATUS CHECK
REM ============================================================
REM 목적: 전체 시스템 상태 점검
REM - CONTROL 서비스 (API, Cloudflare, Ollama)
REM - BOTS 상태
REM - 포트 열림 확인
REM - 외부 접속 가능 여부
REM ============================================================

echo.
echo ================================================================
echo Lee May Control Center - STATUS CHECK
echo ================================================================
echo 시각: %date% %time%
echo ================================================================
echo.

REM ============================================================
REM 1. CONTROL 서비스 상태
REM ============================================================
echo [CONTROL SERVICES]
echo ----------------------------------------------------------------
echo.

echo [1] API Server (5001)
tasklist /FI "WINDOWTITLE eq api_server*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     Status: RUNNING
    netstat -an | find ":5001" | find "LISTENING" >NUL
    if %ERRORLEVEL% EQU 0 (
        echo     Port: 5001 LISTENING
    ) else (
        echo     Port: 5001 NOT LISTENING
    )
) else (
    echo     Status: STOPPED
    echo     Port: 5001 N/A
)
echo.

echo [2] Cloudflare Tunnel
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I "cloudflared.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     Status: RUNNING
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq cloudflared.exe" /FO LIST ^| find "PID:"') do (
        echo     PID: %%a
    )
) else (
    echo     Status: STOPPED
)
echo.

echo [3] Ollama (외부 서버)
curl -s http://ollama.thetheunique.com/api/tags >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     Status: ACCESSIBLE
    echo     URL: http://ollama.thetheunique.com
) else (
    echo     Status: NOT ACCESSIBLE
)
echo.

REM ============================================================
REM 2. BOTS 상태
REM ============================================================
echo [BOTS STATUS]
echo ----------------------------------------------------------------
echo.

echo [1] AI Trading Bot (5000)
tasklist /FI "WINDOWTITLE eq upbit-smart-bot*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     Status: RUNNING
    netstat -an | find ":5000" | find "LISTENING" >NUL
    if %ERRORLEVEL% EQU 0 (
        echo     Port: 5000 LISTENING
    ) else (
        echo     Port: 5000 NOT LISTENING
    )
) else (
    echo     Status: STOPPED (정상 - 현재 비활성)
    echo     Port: 5000 N/A
)
echo.

echo [2] YouTube Learner
tasklist /FI "WINDOWTITLE eq youtube*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     Status: RUNNING
) else (
    echo     Status: STOPPED (정상 - 수동 실행)
)
echo.

REM ============================================================
REM 3. 포트 열림 확인
REM ============================================================
echo [PORT STATUS]
echo ----------------------------------------------------------------
echo.

echo [1] 5001 (API Server)
netstat -an | find ":5001" | find "LISTENING" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     5001: OPEN
) else (
    echo     5001: CLOSED
)

echo [2] 5000 (Trading Bot)
netstat -an | find ":5000" | find "LISTENING" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     5000: OPEN
) else (
    echo     5000: CLOSED (정상 - 현재 비활성)
)

echo [3] 11434 (Ollama - 로컬)
netstat -an | find ":11434" | find "LISTENING" >NUL
if %ERRORLEVEL% EQU 0 (
    echo     11434: OPEN
) else (
    echo     11434: CLOSED (정상 - 외부 서버 사용)
)
echo.

REM ============================================================
REM 4. 외부 접속 확인
REM ============================================================
echo [EXTERNAL ACCESS]
echo ----------------------------------------------------------------
echo.

echo [1] Lee May Control Center
curl -s -o NUL -w "%%{http_code}" https://leemay.thetheunique.com/health >temp_status.txt 2>NUL
set /p STATUS=<temp_status.txt
del temp_status.txt >NUL 2>&1
if "%STATUS%"=="200" (
    echo     URL: https://leemay.thetheunique.com
    echo     Status: ACCESSIBLE (HTTP 200)
) else (
    echo     URL: https://leemay.thetheunique.com
    echo     Status: NOT ACCESSIBLE
)
echo.

echo [2] AI Trading Dashboard
curl -s -o NUL -w "%%{http_code}" https://ai_trading.thetheunique.com >temp_status.txt 2>NUL
set /p STATUS=<temp_status.txt
del temp_status.txt >NUL 2>&1
if "%STATUS%"=="200" (
    echo     URL: https://ai_trading.thetheunique.com
    echo     Status: ACCESSIBLE (HTTP 200)
) else (
    echo     URL: https://ai_trading.thetheunique.com
    echo     Status: NOT ACCESSIBLE (정상 - 5001로 라우팅)
)
echo.

REM ============================================================
REM 5. 종합 판정
REM ============================================================
echo [OVERALL STATUS]
echo ================================================================
echo.

REM 핵심 서비스 체크
set STATUS_OK=1

tasklist /FI "WINDOWTITLE eq api_server*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% NEQ 0 set STATUS_OK=0

tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I "cloudflared.exe" >NUL
if %ERRORLEVEL% NEQ 0 set STATUS_OK=0

if %STATUS_OK% EQU 1 (
    echo 종합 등급: OK
    echo 사유: 핵심 서비스(API, Cloudflare) 모두 정상
    echo.
    echo 권장 조치: 없음
) else (
    echo 종합 등급: FAIL
    echo 사유: 핵심 서비스 일부 미실행
    echo.
    echo 권장 조치:
    echo   1. ops\01_CONTROL_START.bat 실행
    echo   2. 로그 확인: logs\ops_api.log
    echo   3. 방화벽/포트 점검
)
echo.

echo ================================================================
echo STATUS CHECK 완료
echo ================================================================
echo.

pause
