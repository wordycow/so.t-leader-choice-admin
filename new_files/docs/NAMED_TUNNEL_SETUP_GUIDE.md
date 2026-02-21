# 🔧 Cloudflare Named Tunnel 설정 가이드 (Windows)

## 🎯 목표
- 영구 URL 생성 (재시작해도 불변)
- 노트북 GPU 활용
- 한 번 설정으로 영구 사용

---

## 📋 Step 1: Cloudflare 계정 로그인 (1회만)

### 노트북 CMD 또는 PowerShell에서:

```cmd
cloudflared tunnel login
```

**결과:**
- 브라우저가 자동으로 열립니다
- Cloudflare 계정으로 로그인
- "Authorize Cloudflare Tunnel" 페이지에서 승인
- 자동으로 인증 완료됨

✅ 인증 완료 메시지:
```
You have successfully logged in.
If you wish to copy your credentials to a server, they have been saved to:
C:\Users\wordy\.cloudflared\cert.pem
```

---

## 📋 Step 2: Named Tunnel 생성

```cmd
cloudflared tunnel create ollama-stable
```

**결과 예시:**
```
Tunnel credentials written to C:\Users\wordy\.cloudflared\abc123-def456-ghi789.json
Created tunnel ollama-stable with id abc123-def456-ghi789
```

🔑 **중요:** 
- 터널 ID를 복사해두세요: `abc123-def456-ghi789`
- 다음 단계에서 사용됩니다

---

## 📋 Step 3: 설정 파일 생성

### 3.1 설정 파일 위치 확인

```cmd
echo %USERPROFILE%\.cloudflared
```

출력: `C:\Users\wordy\.cloudflared`

### 3.2 config.yml 파일 생성

**메모장으로 생성:**

```cmd
notepad %USERPROFILE%\.cloudflared\config.yml
```

### 3.3 아래 내용 복사 & 붙여넣기:

```yaml
tunnel: abc123-def456-ghi789
credentials-file: C:\Users\wordy\.cloudflared\abc123-def456-ghi789.json

ingress:
  - service: http://localhost:11434
```

⚠️ **주의:**
1. `tunnel:` 뒤에 **Step 2에서 받은 터널 ID** 입력
2. `credentials-file:` 경로에 **같은 터널 ID** 사용
3. YAML은 들여쓰기에 민감합니다 (스페이스 2칸)

### 3.4 파일 저장
- Ctrl+S로 저장
- 메모장 닫기

---

## 📋 Step 4: DNS 라우팅 설정 (자동)

```cmd
cloudflared tunnel route dns ollama-stable ollama-stable
```

**또는 커스텀 서브도메인:**

```cmd
cloudflared tunnel route dns ollama-stable my-ollama
```

**결과:**
- 자동으로 DNS 레코드 생성됨
- Cloudflare가 무료 도메인 제공

---

## 📋 Step 5: 터널 실행 (영구!)

```cmd
cloudflared tunnel run ollama-stable
```

**성공 메시지:**
```
INF Connection established
INF Registered tunnel connection
INF Starting metrics server on 127.0.0.1:XXXX/metrics
```

✅ 이제 터널이 실행됩니다!

---

## 📋 Step 6: 터널 URL 확인

**새 CMD 창에서:**

```cmd
cloudflared tunnel list
```

**결과 예시:**
```
ID                                   NAME           CREATED              CONNECTIONS
abc123-def456-ghi789                 ollama-stable  2026-02-18T04:00:00Z 4
```

**터널 정보 확인:**

```cmd
cloudflared tunnel info ollama-stable
```

**URL 확인:**
- Cloudflare Dashboard: https://dash.cloudflare.com
- Zero Trust → Access → Tunnels
- 터널 URL 복사

**일반적인 URL 형식:**
```
https://abc123-def456-ghi789.cfargotunnel.com
또는
https://ollama-stable.<YOUR-DOMAIN>.com
```

---

## 📋 Step 7: Ollama 서버 실행 확인

**별도 CMD 창에서:**

```cmd
curl http://localhost:11434/api/tags
```

**정상 응답:**
```json
{"models":[{"name":"qwen2.5:7b",...}]}
```

---

## 📋 Step 8: 터널 연결 테스트

**터널 URL로 테스트 (예시):**

```cmd
curl https://abc123-def456-ghi789.cfargotunnel.com/api/tags
```

✅ 같은 응답이 나오면 성공!

---

## 📋 Step 9: 서버에 URL 설정

**이 채팅에서 다음 명령어 실행 요청:**

```
터널 URL을 https://YOUR-TUNNEL-URL.cfargotunnel.com 로 업데이트해줘
```

또는 직접:

```bash
cd /home/user/webapp
echo "OLLAMA_URL=https://YOUR-TUNNEL-URL.cfargotunnel.com" > .env
echo "OLLAMA_MODEL=qwen2.5:7b-instruct" >> .env
pkill -f upbit-smart-bot
python3 upbit-smart-bot-v8.0-ULTIMATE.py &
```

---

## 🔄 터널 자동 시작 (Windows)

### 방법 1: 시작 프로그램에 추가

1. `Win + R` → `shell:startup`
2. 우클릭 → 새로 만들기 → 바로 가기
3. 위치:
```
C:\Windows\System32\cmd.exe /c cloudflared tunnel run ollama-stable
```
4. 이름: `Ollama Tunnel`

### 방법 2: 배치 파일 생성

**ollama_tunnel.bat 생성:**

```batch
@echo off
echo Starting Ollama Tunnel...
cloudflared tunnel run ollama-stable
pause
```

**더블클릭으로 실행**

### 방법 3: Windows 서비스 등록 (고급)

```cmd
REM 관리자 권한 CMD에서
cloudflared service install
```

---

## ✅ 완료 체크리스트

- [ ] `cloudflared tunnel login` 완료
- [ ] `cloudflared tunnel create ollama-stable` 완료
- [ ] `config.yml` 파일 생성 완료
- [ ] 터널 ID를 config.yml에 입력
- [ ] `cloudflared tunnel run ollama-stable` 실행
- [ ] `cloudflared tunnel list`로 URL 확인
- [ ] 로컬 Ollama 서버 실행 중
- [ ] 터널 URL로 접속 테스트 성공
- [ ] 서버 .env 파일에 URL 설정 완료

---

## 🎉 완료 후

**장점:**
- ✅ 영구 URL (재시작해도 불변)
- ✅ 노트북 GPU 활용
- ✅ 빠른 응답 (2-5초)
- ✅ 더 이상 URL 변경 걱정 없음

**터널 재시작 방법:**
```cmd
Ctrl+C (현재 터널 중지)
cloudflared tunnel run ollama-stable (재시작)
```

URL은 절대 변하지 않습니다! 🎊

---

## 🆘 문제 해결

### 문제: "tunnel not found"
→ `cloudflared tunnel list`로 이름 확인

### 문제: "502 Bad Gateway"
→ Ollama 서버가 실행 중인지 확인
```cmd
curl http://localhost:11434/api/tags
```

### 문제: "connection refused"
→ config.yml의 service 주소 확인
```yaml
service: http://localhost:11434
```

### 문제: "authentication failed"
→ 다시 로그인
```cmd
cloudflared tunnel login
```

---

## 📞 다음 단계

1. 위 단계를 차례대로 진행
2. 터널 URL을 확인
3. 이 채팅에 터널 URL 공유
4. 자동으로 서버 설정 완료!

🚀 시작하세요!

