# 이메이 백그라운드 실행 가이드

## 📦 포함된 파일

1. **start_emay_background.bat** - 백그라운드 서버 시작 (창 보임)
2. **start_emay_silent.vbs** - 완전 백그라운드 시작 (창 안 보임)
3. **stop_emay.bat** - 서버 종료

---

## 🚀 사용 방법

### 방법 1: 백그라운드 시작 (로그 확인 가능)

1. `start_emay_background.bat` 더블클릭
2. 창이 뜨면서 서버 시작 → "성공" 메시지 확인
3. 창을 닫아도 서버는 백그라운드에서 계속 실행됨

### 방법 2: 완전 백그라운드 (창 없음)

1. `start_emay_silent.vbs` 더블클릭
2. 아무 창도 안 뜸 → 백그라운드에서 자동 실행
3. 작업 관리자에서 `pythonw.exe` 프로세스 확인 가능

---

## 🛑 서버 종료

`stop_emay.bat` 더블클릭 → 백그라운드 서버 종료

---

## 🔧 Windows 부팅 시 자동 시작 (선택)

### 방법 1: 시작 프로그램에 등록

1. `Win + R` → `shell:startup` 입력
2. 열린 폴더에 `start_emay_silent.vbs` **바로가기** 복사
3. 재부팅 시 자동으로 서버 시작됨

### 방법 2: 작업 스케줄러 (고급)

1. `Win + R` → `taskschd.msc` 입력
2. 우측 "기본 작업 만들기" 클릭
3. 설정:
   - 이름: `이메이 자동 시작`
   - 트리거: `컴퓨터 시작 시`
   - 작업: `프로그램 시작`
   - 프로그램: `C:\emay_project\emay\start_emay_silent.vbs`
4. 완료 → 재부팅하면 자동 시작

---

## 📋 로그 확인

백그라운드 실행 중 오류가 나면:

```
C:\emay_project\emay\emay_server.log
```

파일을 열어서 오류 메시지 확인

---

## ❓ 문제 해결

### Q1. "Python이 PATH에 없습니다" 오류
**A:** Python 재설치 시 "Add Python to PATH" 체크

### Q2. 서버가 시작되지 않음
**A:** 
1. `emay_server.log` 파일 확인
2. 수동 실행으로 오류 확인: `python api_server.py`

### Q3. 포트 5001이 이미 사용 중
**A:**
```bash
netstat -ano | findstr :5001
taskkill /F /PID <PID번호>
```

---

## 🎯 파일 배치

```
C:\emay_project\emay\
├── start_emay_background.bat   ← 백그라운드 시작
├── start_emay_silent.vbs       ← 창 없이 시작
├── stop_emay.bat               ← 종료
├── emay_server.log             ← 로그 (자동 생성)
└── emay_server.pid             ← PID (자동 생성)
```

---

✨ **이제 터미널 닫아도 서버가 계속 돌아갑니다!**
