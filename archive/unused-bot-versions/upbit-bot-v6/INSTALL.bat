@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v6.0 - 설치

cd /d "%~dp0"

cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║    🤖 업비트 스마트 봇 v6.0                  ║
echo ║         자동 설치 프로그램                   ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo 📦 필수 구성 요소 설치를 시작합니다...
echo.

REM Step 1: Python 확인
echo [1/5] Python 설치 확인 중...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ❌ Python이 설치되어 있지 않습니다!
    echo.
    echo 📥 Python 설치 방법:
    echo  1. https://www.python.org/downloads/ 접속
    echo  2. "Download Python" 버튼 클릭
    echo  3. 다운로드한 설치 파일 실행
    echo  4. ⚠️  중요: "Add Python to PATH" 체크박스 체크!
    echo  5. "Install Now" 클릭
    echo  6. 설치 완료 후 컴퓨터 재시작
    echo  7. 다시 이 설치 파일 실행
    echo.
    echo 브라우저를 열어 Python 다운로드 페이지로 이동합니다...
    timeout /t 3 >nul
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo    ✅ Python 설치 확인 완료
echo.

REM Step 2: pip 업그레이드
echo [2/5] pip 업그레이드 중...
python -m pip install --upgrade pip --quiet
if %errorLevel% neq 0 (
    echo    ⚠️  pip 업그레이드 실패 (무시하고 계속)
) else (
    echo    ✅ pip 업그레이드 완료
)
echo.

REM Step 3: requirements.txt 확인
echo [3/5] requirements.txt 파일 확인 중...
if not exist "requirements.txt" (
    echo    ⚠️  requirements.txt 파일이 없습니다. 기본 라이브러리 생성 중...
    (
        echo Flask
        echo flask-cors
        echo pyupbit
        echo pandas
        echo numpy
        echo requests
    ) > requirements.txt
)
echo    ✅ requirements.txt 확인 완료
echo.

REM Step 4: 라이브러리 설치
echo [4/5] Python 라이브러리 설치 중... (약 2-5분 소요)
echo.
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo.
    echo ❌ 라이브러리 설치 실패!
    echo.
    echo 📥 해결 방법:
    echo  1. 인터넷 연결 확인
    echo  2. 방화벽/백신 프로그램 일시 비활성화
    echo  3. 관리자 권한으로 다시 실행:
    echo     - 이 파일에 우클릭
    echo     - "관리자 권한으로 실행" 선택
    echo  4. 또는 수동 설치:
    echo     - 명령 프롬프트(cmd) 열기
    echo     - 다음 명령어 입력:
    echo       pip install Flask flask-cors pyupbit pandas numpy requests
    echo.
    pause
    exit /b 1
)
echo.
echo    ✅ 라이브러리 설치 완료
echo.

REM Step 5: 설치 확인
echo [5/5] 설치 확인 중...
python -c "import flask, flask_cors, pyupbit, pandas, numpy, requests; print('    ✅ 모든 라이브러리 정상 작동')" 2>nul
if %errorLevel% neq 0 (
    echo    ⚠️  일부 라이브러리 로드 실패
    echo       하지만 START.cmd 실행 시 자동으로 재시도됩니다
)
echo.

echo ═══════════════════════════════════════════════
echo.
echo ✅ 설치가 완료되었습니다!
echo.
echo 📌 다음 단계:
echo  1. 'START.cmd' 파일 더블클릭
echo  2. 브라우저에서 http://localhost:5000 자동으로 열림
echo  3. API 키 설정 후 봇 시작
echo.
echo 📚 더 자세한 설명:
echo  - README.md 파일 참고
echo  - 문제 발생 시 스크린샷과 함께 문의
echo.
echo ═══════════════════════════════════════════════
echo.

pause
