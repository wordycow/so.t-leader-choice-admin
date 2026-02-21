# 🔄 Ollama & Tunnel 자동 시작 가이드 (Windows)

## 📋 목표
1. Ollama 서버 자동 재시작 (종료 시)
2. Cloudflare Tunnel 자동 재시작 (종료 시)
3. 컴퓨터 부팅 시 자동 실행

---

## 📦 제공 파일 (4개)

### 1. `ollama_auto_restart.bat` - Ollama 자동 재시작
- Ollama 서버가 종료되면 즉시 재시작
- 5초마다 상태 체크
- 무한 루프

### 2. `tunnel_auto_restart.bat` - Tunnel 자동 재시작
- Named Tunnel이 종료되면 즉시 재시작
- 5초마다 상태 체크
- 무한 루프

### 3. `startup_all.bat` - 부팅 시 모두 실행
- Ollama + Tunnel 동시 시작
- 백그라운드 실행
- 로그 파일 생성

### 4. `stop_all.bat` - 모두 중지
- Ollama + Tunnel 안전 종료

---

## 🚀 빠른 시작

### Step 1: 배치 파일 다운로드

아래 4개 파일을 `C:\ollama\` 폴더에 저장:
- ollama_auto_restart.bat
- tunnel_auto_restart.bat
- startup_all.bat
- stop_all.bat

### Step 2: 수동 테스트

```cmd
# Ollama 자동 재시작 테스트
C:\ollama\ollama_auto_restart.bat

# Tunnel 자동 재시작 테스트 (새 창에서)
C:\ollama\tunnel_auto_restart.bat
```

### Step 3: 부팅 시 자동 실행 설정

**방법 A: 시작 프로그램 (간단)**

1. `Win + R` → `shell:startup` 입력
2. 바로가기 생성:
   - 대상: `C:\ollama\startup_all.bat`
   - 이름: `Ollama & Tunnel Auto Start`
3. 재부팅 테스트

**방법 B: 작업 스케줄러 (고급)**

1. `Win + R` → `taskschd.msc`
2. 작업 만들기:
   - 이름: `Ollama Tunnel Auto Start`
   - 트리거: 시스템 시작 시
   - 동작: `C:\ollama\startup_all.bat` 실행
   - 조건: 전원 연결 시에만 (선택)

---

## 📄 파일 내용

### ollama_auto_restart.bat

```batch
@echo off
title Ollama Auto Restart
echo ====================================
echo Ollama 자동 재시작 스크립트
echo ====================================
echo.

:loop
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [%date% %time%] Ollama 실행 중...
    timeout /t 5 /nobreak >nul
    goto loop
) else (
    echo [%date% %time%] Ollama 종료 감지! 재시작 중...
    start /B ollama serve
    echo [%date% %time%] Ollama 재시작 완료
    timeout /t 10 /nobreak >nul
    goto loop
)
```

### tunnel_auto_restart.bat

```batch
@echo off
title Cloudflare Tunnel Auto Restart
echo ====================================
echo Cloudflare Tunnel 자동 재시작
echo ====================================
echo.

:loop
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I /N "cloudflared.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [%date% %time%] Tunnel 실행 중...
    timeout /t 5 /nobreak >nul
    goto loop
) else (
    echo [%date% %time%] Tunnel 종료 감지! 재시작 중...
    start /B cloudflared tunnel run ollama-stable
    echo [%date% %time%] Tunnel 재시작 완료
    timeout /t 10 /nobreak >nul
    goto loop
)
```

### startup_all.bat

```batch
@echo off
title Ollama & Tunnel Startup
echo ====================================
echo Ollama + Tunnel 부팅 시 자동 실행
echo ====================================
echo.

REM 로그 디렉토리 생성
if not exist "C:\ollama\logs" mkdir "C:\ollama\logs"

REM Ollama 시작
echo [%date% %time%] Ollama 시작 중...
start /B ollama serve >> "C:\ollama\logs\ollama.log" 2>&1
timeout /t 5 /nobreak >nul

REM Tunnel 시작
echo [%date% %time%] Tunnel 시작 중...
start /B cloudflared tunnel run ollama-stable >> "C:\ollama\logs\tunnel.log" 2>&1
timeout /t 3 /nobreak >nul

REM 자동 재시작 스크립트 실행 (백그라운드)
echo [%date% %time%] 자동 재시작 감시 시작...
start /MIN cmd /c "C:\ollama\ollama_auto_restart.bat"
start /MIN cmd /c "C:\ollama\tunnel_auto_restart.bat"

echo.
echo ====================================
echo 모든 서비스 시작 완료!
echo ====================================
echo.
echo Ollama URL: http://localhost:11434
echo Tunnel URL: http://ollama.thetheunique.com
echo.
echo 로그 위치: C:\ollama\logs\
echo.
timeout /t 5
exit
```

### stop_all.bat

```batch
@echo off
title Stop Ollama & Tunnel
echo ====================================
echo Ollama + Tunnel 중지
echo ====================================
echo.

echo Ollama 중지 중...
taskkill /F /IM ollama.exe 2>nul
if %ERRORLEVEL%==0 (
    echo ✓ Ollama 중지됨
) else (
    echo ✗ Ollama가 실행 중이지 않음
)

echo.
echo Tunnel 중지 중...
taskkill /F /IM cloudflared.exe 2>nul
if %ERRORLEVEL%==0 (
    echo ✓ Tunnel 중지됨
) else (
    echo ✗ Tunnel이 실행 중이지 않음
)

echo.
echo 자동 재시작 스크립트 중지 중...
taskkill /FI "WINDOWTITLE eq Ollama Auto Restart" 2>nul
taskkill /FI "WINDOWTITLE eq Cloudflare Tunnel Auto Restart" 2>nul

echo.
echo ====================================
echo 모든 서비스 중지 완료!
echo ====================================
pause
```

---

## 🔧 사용 방법

### 일상 사용

**시작:**
- 더블클릭: `startup_all.bat`
- 또는 자동 부팅 (설정 후)

**중지:**
- 더블클릭: `stop_all.bat`

**상태 확인:**
```cmd
# Ollama 확인
curl http://localhost:11434/api/tags

# Tunnel 확인
curl http://ollama.thetheunique.com/api/tags
```

---

## 📊 로그 확인

```cmd
# Ollama 로그
type C:\ollama\logs\ollama.log

# Tunnel 로그
type C:\ollama\logs\tunnel.log

# 실시간 모니터링 (PowerShell)
Get-Content C:\ollama\logs\ollama.log -Wait -Tail 20
```

---

## 🆘 문제 해결

### 문제: "Access Denied" 오류
→ 관리자 권한으로 실행

### 문제: 배치 파일이 즉시 닫힘
→ 파일 끝에 `pause` 추가

### 문제: 부팅 시 자동 실행 안 됨
→ 시작 프로그램 경로 확인
→ `shell:startup` 폴더에 바로가기 확인

### 문제: Ollama/Tunnel 중복 실행
→ `stop_all.bat` 실행 후 재시작

---

## ✅ 완료 체크리스트

- [ ] 4개 배치 파일 생성
- [ ] `C:\ollama\` 폴더에 저장
- [ ] `ollama_auto_restart.bat` 테스트
- [ ] `tunnel_auto_restart.bat` 테스트
- [ ] `startup_all.bat` 테스트
- [ ] 시작 프로그램에 등록
- [ ] 재부팅 테스트
- [ ] 로그 확인

---

## 🎯 예상 결과

✅ Ollama 종료 → 5초 내 자동 재시작
✅ Tunnel 종료 → 5초 내 자동 재시작
✅ 컴퓨터 부팅 → 자동 실행
✅ URL 불변: http://ollama.thetheunique.com

---

## 💡 고급 팁

### Windows 서비스로 등록 (최고급)

```cmd
REM NSSM (Non-Sucking Service Manager) 사용
nssm install OllamaService "C:\Windows\System32\cmd.exe" "/c ollama serve"
nssm install TunnelService "C:\Windows\System32\cmd.exe" "/c cloudflared tunnel run ollama-stable"

REM 서비스 시작
nssm start OllamaService
nssm start TunnelService
```

다운로드: https://nssm.cc/download

---

