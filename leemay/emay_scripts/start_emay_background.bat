@echo off
REM 이메이 API 서버 백그라운드 시작 스크립트
echo ========================================
echo 이메이 백그라운드 서버 시작 중...
echo ========================================

REM Python 경로 확인
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 프로젝트 경로로 이동
cd /d C:\emay_project\emay

REM 서버 실행 (백그라운드)
echo.
echo [1/2] API 서버 시작 중...
start /B pythonw.exe api_server.py > emay_server.log 2>&1

REM PID 저장
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FO LIST ^| findstr "PID"') do (
    echo %%a > emay_server.pid
    echo     └─ PID: %%a
)

echo.
echo [2/2] 서버 상태 확인 중...
timeout /t 3 /nobreak >nul

REM 헬스체크
curl -s http://localhost:5001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo     └─ [성공] 서버 실행 중: http://localhost:5001
) else (
    echo     └─ [경고] 서버 시작 중... 5초 후 다시 확인하세요.
)

echo.
echo ========================================
echo 이메이 백그라운드 서버 시작 완료!
echo ========================================
echo.
echo 로그 파일: C:\emay_project\emay\emay_server.log
echo PID 파일: C:\emay_project\emay\emay_server.pid
echo.
echo 종료하려면: stop_emay.bat 실행
echo.
pause
