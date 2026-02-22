@echo off
REM 이메이 API 서버 종료 스크립트
echo ========================================
echo 이메이 서버 종료 중...
echo ========================================

REM PID 파일 확인
if not exist "C:\emay_project\emay\emay_server.pid" (
    echo [경고] PID 파일이 없습니다.
    echo 모든 pythonw.exe 프로세스를 종료합니다.
    taskkill /F /IM pythonw.exe >nul 2>&1
    echo [완료] 종료되었습니다.
    pause
    exit /b 0
)

REM PID로 프로세스 종료
for /f %%a in (C:\emay_project\emay\emay_server.pid) do (
    echo [종료] PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM PID 파일 삭제
del C:\emay_project\emay\emay_server.pid

echo.
echo ========================================
echo 이메이 서버 종료 완료!
echo ========================================
echo.
pause
