@echo off
chcp 65001 > nul
title 소스 코드 암호화 도구

cd /d "%~dp0"

cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║    🔒 소스 코드 보호 도구                    ║
echo ║         PyArmor 자동 암호화                  ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo ⚠️  주의사항:
echo  • 이 스크립트는 소스 코드를 암호화합니다
echo  • 암호화 후 원본은 안전하게 백업하세요
echo  • 암호화된 파일은 편집할 수 없습니다
echo.
echo ═══════════════════════════════════════════════
echo.

pause

echo.
echo [1/5] PyArmor 설치 확인 중...
python -c "import pyarmor" >nul 2>&1
if %errorLevel% neq 0 (
    echo    ⚠️  PyArmor가 설치되지 않았습니다
    echo    📥 자동 설치 중...
    pip install pyarmor
    if %errorLevel% neq 0 (
        echo.
        echo ❌ PyArmor 설치 실패!
        echo.
        echo 수동 설치 방법:
        echo  pip install pyarmor
        pause
        exit /b 1
    )
)
echo    ✅ PyArmor 설치 확인

echo.
echo [2/5] 백업 생성 중...
if not exist "backup" mkdir backup
xcopy /E /I /Y "*.py" "backup\" >nul 2>&1
xcopy /E /I /Y "templates" "backup\templates\" >nul 2>&1
echo    ✅ 백업 완료: backup\ 폴더

echo.
echo [3/5] 소스 코드 암호화 중...
echo    (약 30초 소요...)
pyarmor gen -O protected upbit-smart-bot-v6.py
if %errorLevel% neq 0 (
    echo.
    echo ❌ 암호화 실패!
    pause
    exit /b 1
)
echo    ✅ 암호화 완료

echo.
echo [4/5] 필수 파일 복사 중...
if not exist "protected\templates" mkdir protected\templates
copy "templates\*.html" "protected\templates\" >nul 2>&1
copy "START.cmd" "protected\" >nul 2>&1
copy "INSTALL.bat" "protected\" >nul 2>&1
copy "설치시작.cmd" "protected\" >nul 2>&1
copy "requirements.txt" "protected\" >nul 2>&1
copy "README.md" "protected\" >nul 2>&1
copy "*.md" "protected\" >nul 2>&1
echo    ✅ 파일 복사 완료

echo.
echo [5/5] 배포 패키지 생성 중...
cd protected
if exist "..\upbit-bot-v6.0-PROTECTED.zip" del "..\upbit-bot-v6.0-PROTECTED.zip"
powershell -Command "Compress-Archive -Path * -DestinationPath ..\upbit-bot-v6.0-PROTECTED.zip -Force"
cd ..
echo    ✅ 패키지 생성 완료

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║  ✅ 암호화 완료!                             ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo 📦 생성된 파일:
echo  • protected\              (암호화된 소스)
echo  • backup\                 (원본 백업)
echo  • upbit-bot-v6.0-PROTECTED.zip  (배포용)
echo.
echo 📤 배포 방법:
echo  1. upbit-bot-v6.0-PROTECTED.zip 만 친구들에게 전달
echo  2. 원본 소스는 절대 공유하지 마세요!
echo  3. backup\ 폴더는 안전하게 보관
echo.
echo 🧪 테스트:
echo  1. protected\ 폴더로 이동
echo  2. START.cmd 실행
echo  3. 정상 작동 확인
echo.
echo ⚠️  주의:
echo  • 암호화된 파일은 편집 불가
echo  • 수정이 필요하면 원본을 수정 후 재암호화
echo.
echo ═══════════════════════════════════════════════
echo.

pause
