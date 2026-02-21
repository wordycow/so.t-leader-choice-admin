@echo off
REM ============================================================
REM Lee May Control Center - CONTROL START
REM ============================================================
REM 목적: 핵심 제어 서비스만 시작 (항상 켜져 있어야 함)
REM - API Server (포트 5001) - Lee May Training Center
REM - Cloudflare Tunnel (외부 접속용)
REM - MongoDB Atlas (원격 - 자동 연결)
REM - Ollama LLM (외부 서버 - 연결 확인만)
REM ============================================================

echo.
echo ========================================
echo Lee May Control Center - CONTROL START
echo ========================================
echo.

REM 작업 디렉토리 이동
cd /d C:\leemay_project

REM ============================================================
REM 1. 환경 확인
REM ============================================================
echo [1/4] 환경 확인 중...
echo.

REM Python 설치 확인
python --version >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python이 설치되어 있지 않습니다
    echo         Python 3.8 이상 설치 후 다시 실행하세요
    echo.
    pause
    exit /b 1
)

REM 필수 파일 확인
if not exist "api_server.py" (
    echo [ERROR] api_server.py 파일을 찾을 수 없습니다
    echo         작업 디렉토리: %CD%
    echo.
    pause
    exit /b 1
)

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "learning_logs" mkdir learning_logs

echo [OK] 환경 확인 완료
echo.

REM ============================================================
REM 2. Ollama 연결 확인
REM ============================================================
echo [2/4] Ollama 외부 서버 연결 확인 중...
echo URL: http://ollama.thetheunique.com
echo.

curl -s -o NUL -w "%%{http_code}" http://ollama.thetheunique.com/api/tags >temp_ollama.txt 2>NUL
set /p OLLAMA_STATUS=<temp_ollama.txt
del temp_ollama.txt >NUL 2>&1

if "%OLLAMA_STATUS%"=="200" (
    echo [OK] Ollama 서버 접속 가능
) else (
    echo [WARN] Ollama 서버 접속 실패 (HTTP %OLLAMA_STATUS%)
    echo        계속 진행하지만 AI 기능이 제한될 수 있습니다
)
echo.

REM ============================================================
REM 3. API Server 시작 (포트 5001)
REM ============================================================
echo [3/4] API Server 시작 중...
echo 포트: 5001
echo 파일: api_server.py
echo.

REM 이미 실행 중인지 확인
tasklist /FI "WINDOWTITLE eq api_server*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [WARN] API Server가 이미 실행 중입니다
    echo        재시작하려면 먼저 종료하세요
    echo.
) else (
    REM API Server 백그라운드 실행
    start "api_server" /MIN python api_server.py
    
    REM 시작 대기
    timeout /t 3 /nobreak >NUL
    
    REM 시작 확인
    netstat -an | find ":5001" | find "LISTENING" >NUL
    if %ERRORLEVEL% EQU 0 (
        echo [OK] API Server 시작 완료
        echo      로컬: http://localhost:5001
        echo      외부: https://leemay.thetheunique.com
    ) else (
        echo [ERROR] API Server 시작 실패
        echo         로그 확인: logs\api_server.log
    )
    echo.
)

REM ============================================================
REM 4. Cloudflare Tunnel 시작
REM ============================================================
echo [4/4] Cloudflare Tunnel 시작 중...
echo Config: config.yml
echo.

REM 이미 실행 중인지 확인
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I "cloudflared.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [WARN] Cloudflare Tunnel이 이미 실행 중입니다
    echo        재시작하려면 먼저 종료하세요
    echo.
) else (
    REM cloudflared 설치 확인
    where cloudflared >NUL 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] cloudflared가 설치되어 있지 않습니다
        echo         다운로드: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
        echo.
        echo [INFO] Cloudflare Tunnel 없이 계속 진행합니다
        echo        로컬 접속만 가능: http://localhost:5001
        echo.
    ) else (
        REM config.yml 확인
        if not exist "config.yml" (
            echo [ERROR] config.yml 파일을 찾을 수 없습니다
            echo         Cloudflare Tunnel 설정 후 다시 실행하세요
            echo.
            echo [INFO] Cloudflare Tunnel 없이 계속 진행합니다
            echo        로컬 접속만 가능: http://localhost:5001
            echo.
        ) else (
            REM Cloudflare Tunnel 백그라운드 실행
            start "cloudflared" /MIN cloudflared tunnel --config config.yml run
            
            REM 시작 대기
            timeout /t 3 /nobreak >NUL
            
            REM 시작 확인
            tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I "cloudflared.exe" >NUL
            if %ERRORLEVEL% EQU 0 (
                echo [OK] Cloudflare Tunnel 시작 완료
                echo      외부 접속 가능: https://leemay.thetheunique.com
            ) else (
                echo [WARN] Cloudflare Tunnel 시작 실패
                echo        로컬 접속만 가능: http://localhost:5001
            )
            echo.
        )
    )
)

REM ============================================================
REM 완료 및 상태 확인
REM ============================================================
echo ========================================
echo CONTROL START 완료
echo ========================================
echo.

echo [핵심 서비스 상태]
echo.

echo API Server (5001):
tasklist /FI "WINDOWTITLE eq api_server*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo   ✓ 실행 중
    echo   → http://localhost:5001
) else (
    echo   ✗ 정지
)
echo.

echo Cloudflare Tunnel:
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I "cloudflared.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo   ✓ 실행 중
    echo   → https://leemay.thetheunique.com
) else (
    echo   ✗ 정지 (로컬 접속만 가능)
)
echo.

echo ========================================
echo 다음 단계:
echo   1. 상태 확인: ops\99_STATUS.bat
echo   2. 봇 시작: ops\02_BOTS_START.bat
echo   3. 웹 접속: http://localhost:5001
echo ========================================
echo.

pause
