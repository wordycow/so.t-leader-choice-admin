@echo off
setlocal
set BASE=C:\leemay_project
set LOG=%BASE%\logs\ops_update.log

echo.>>"%LOG%"
echo ==================================================>>"%LOG%"
echo [%%date%% %%time%%] APPLY UPDATE START>>"%LOG%"
echo ==================================================>>"%LOG%"

cd /d "%BASE%" || (
  echo [ERROR] cd fail>>"%LOG%"
  exit /b 1
)

REM 1) 최신 코드 받기 (git 사용 중이면)
where git >nul 2>nul
if %errorlevel%==0 (
  echo [STEP] git pull>>"%LOG%"
  git pull origin main >>"%LOG%" 2>>&1
) else (
  echo [WARN] git not found - skip git pull>>"%LOG%"
)

REM 2) 의존성 설치 (필요하면)
echo [STEP] pip install>>"%LOG%"
python -m pip install -r "%BASE%\requirements.txt" >>"%LOG%" 2>>&1

REM 3) 5001 재시작
echo [STEP] restart 5001>>"%LOG%"
call "%BASE%\ops\04_OPS_RESTART_5001.bat" >>"%LOG%" 2>>&1

echo [DONE] APPLY UPDATE END>>"%LOG%"
endlocal
exit /b 0