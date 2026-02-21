# 🔧 Ollama 로컬 연결 체크리스트

## 문제 상황
- Cloudflare 터널은 시작됨: `https://handles-convenience-nylon-trout.trycloudflare.com`
- 하지만 터널을 통한 Ollama 연결이 타임아웃됨

## ✅ 노트북에서 확인할 사항

### 1️⃣ Ollama 서버가 실행 중인가?

**Windows PowerShell 또는 CMD에서 실행:**
```cmd
curl http://localhost:11434/api/tags
```

**정상 응답 예시:**
```json
{"models":[{"name":"qwen2.5:7b","modified_at":"2026-02-17T23:45:32+09:00",...}]}
```

**만약 응답이 없으면:**
```cmd
# Ollama 서버 시작
ollama serve
```

---

### 2️⃣ Ollama가 포트 11434에서 대기 중인가?

```cmd
netstat -ano | findstr :11434
```

**정상 출력 예시:**
```
TCP    0.0.0.0:11434    0.0.0.0:0    LISTENING    12345
```

---

### 3️⃣ Cloudflare 터널이 올바른 포트에 연결되어 있는가?

터널 로그에서 확인:
```
Settings: map[ha-connections:1 protocol:quic url:http://localhost:11434]
```
✅ `url:http://localhost:11434` 가 표시되면 정상

---

### 4️⃣ 방화벽 문제?

Windows 방화벽에서 Ollama를 허용했는지 확인:
```cmd
# 방화벽 규칙 추가 (관리자 권한 필요)
netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=TCP localport=11434
```

---

## 🔄 해결 방법

### 방법 A: Ollama 재시작 (추천)

1. **Ollama 서버 중지:**
   ```cmd
   taskkill /F /IM ollama.exe
   ```

2. **Ollama 서버 재시작:**
   ```cmd
   ollama serve
   ```

3. **새 터미널에서 터널 재시작:**
   ```cmd
   cloudflared tunnel --url http://localhost:11434
   ```

4. **노트북에서 로컬 테스트:**
   ```cmd
   curl http://localhost:11434/api/tags
   ```

---

### 방법 B: 환경 변수 확인

Ollama가 올바른 호스트를 사용하는지 확인:
```cmd
set OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

---

### 방법 C: 터널 대신 공개 IP 사용 (보안 주의!)

만약 공유기 포트포워딩이 가능하다면:
1. 공유기에서 외부 포트 → 내부 11434 포트포워딩 설정
2. 공인 IP 확인: `curl ifconfig.me`
3. 서버에 공인 IP:11434 설정

⚠️ **주의:** 보안을 위해 API 키 인증 설정 필요!

---

## 📊 현재 권장 해결 순서

1. 노트북에서 `curl http://localhost:11434/api/tags` 실행
   - 응답 없음 → Ollama 재시작 (`ollama serve`)
   - 응답 있음 → 아래 계속

2. Cloudflare 터널 재시작:
   ```cmd
   # Ctrl+C로 기존 터널 종료 후
   cloudflared tunnel --url http://localhost:11434
   ```

3. 새 터널 URL 확인 후 이 채팅에 공유

4. 서버 업데이트 스크립트 실행:
   ```bash
   cd /home/user/webapp
   ./update_ollama_url.sh https://새로운-URL.trycloudflare.com
   ```

---

## 🆘 문제가 계속되면?

### 임시 해결책: DB 전용 모드
Ollama 없이도 Emei의 153개 DB 답변은 정상 작동합니다:
- ✅ 일상 대화, 감정 대응, 트레이딩 조언
- ✅ 수동 학습: `학습: 질문 => 답변`
- ✅ 모든 대화 자동 저장

단, AI 생성 답변은 사용할 수 없습니다.

---

## 📞 연락 방법

위 단계를 진행하신 후:
1. `curl http://localhost:11434/api/tags` 결과
2. 새 터널 URL
3. 에러 메시지 (있다면)

를 이 채팅에 공유해주시면 즉시 해결하겠습니다! 🚀
