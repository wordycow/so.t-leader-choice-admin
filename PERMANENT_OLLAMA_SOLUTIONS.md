# 🔧 Ollama 영구 연결 해결 방안

## 문제점
- Cloudflare Quick Tunnel은 매번 URL이 바뀜 (임시 터널)
- 터널 끊김 시마다 수동 업데이트 필요
- 프로덕션 환경에 부적합

## ✅ 해결 방안 (우선순위별)

---

### 방안 1: 🏆 Cloudflare Named Tunnel (추천) - 영구 URL

**장점:**
- ✅ **영구 URL** - 재시작해도 URL 불변
- ✅ 무료 (Cloudflare 계정 필요)
- ✅ HTTPS 자동 적용
- ✅ 안정적 연결
- ✅ 방화벽 우회

**단점:**
- ❌ Cloudflare 계정 필요 (1회만)
- ❌ 초기 설정 5분

**설치 방법 (노트북):**

```bash
# 1. Cloudflare 계정으로 로그인 (1회만)
cloudflared tunnel login

# 2. Named Tunnel 생성
cloudflared tunnel create ollama-tunnel

# 3. 설정 파일 생성 (~/.cloudflared/config.yml)
cat > ~/.cloudflared/config.yml << 'YAML'
tunnel: <TUNNEL-ID-여기-입력>
credentials-file: ~/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: ollama.your-domain.com  # 또는 Cloudflare 자동 도메인
    service: http://localhost:11434
  - service: http_status:404
YAML

# 4. DNS 레코드 설정 (자동)
cloudflared tunnel route dns ollama-tunnel ollama.your-domain.com

# 5. 터널 실행 (영구 URL로 연결됨!)
cloudflared tunnel run ollama-tunnel
```

**결과:** `https://ollama.your-domain.com` - 영구 불변 URL!

---

### 방안 2: 🐳 샌드박스 내부에 Ollama 설치 (가장 간단)

**장점:**
- ✅ **터널 불필요** - localhost만 사용
- ✅ 초고속 응답 (0.5초)
- ✅ 완전 독립 실행
- ✅ 설정 변경 없음

**단점:**
- ❌ 샌드박스 GPU 없음 (CPU 전용)
- ❌ 느린 추론 속도 (CPU)
- ❌ 큰 모델 불가 (메모리 제한)

**설치 방법 (샌드박스):**

```bash
# 1. Ollama 설치 (1회만)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Ollama 서버 시작
ollama serve &

# 3. 작은 모델 다운로드 (CPU 최적화)
ollama pull qwen2.5:1.5b    # 1.5B 파라미터 (빠름)
# 또는
ollama pull gemma2:2b       # 2B 파라미터

# 4. .env 파일 수정
echo "OLLAMA_URL=http://127.0.0.1:11434" > .env
echo "OLLAMA_MODEL=qwen2.5:1.5b" >> .env

# 5. 서버 재시작
pkill -f upbit-smart-bot
python3 upbit-smart-bot-v8.0-ULTIMATE.py &
```

**예상 성능:**
- 1.5B 모델: 3-8초 응답 (CPU)
- 2B 모델: 5-12초 응답 (CPU)

---

### 방안 3: 🌐 Public IP + 포트포워딩 (노트북 공인 IP)

**장점:**
- ✅ 직접 연결 (중간 서버 없음)
- ✅ 빠른 속도 (터널 오버헤드 없음)
- ✅ 완전 제어 가능

**단점:**
- ❌ 공유기 포트포워딩 설정 필요
- ❌ 고정 IP 필요 (또는 DDNS)
- ❌ 보안 위험 (인터넷 노출)
- ❌ 공유기 관리자 권한 필요

**설정 방법:**

1. **공유기 설정:**
   - 외부 포트 11434 → 내부 192.168.x.x:11434
   - (보안을 위해 다른 포트 권장: 예 18888 → 11434)

2. **Ollama 공개 실행:**
```bash
# 노트북에서
set OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

3. **공인 IP 확인:**
```bash
curl ifconfig.me
# 결과: 123.45.67.89
```

4. **서버 .env 설정:**
```bash
OLLAMA_URL=http://123.45.67.89:11434
```

⚠️ **보안 주의:** 방화벽 규칙 + API 키 인증 필수!

---

### 방안 4: 🔄 Ollama를 클라우드 서버에 배포

**서비스 옵션:**
- Replicate.com (유료, GPU, API 형태)
- RunPod (GPU 대여)
- Lambda Labs (GPU 클라우드)
- AWS/GCP/Azure (비쌈)

**비용:**
- Replicate: $0.0003/초 (~$1/시간)
- RunPod: $0.20/시간 (GPU)

---

## 🎯 추천 방안 (우선순위)

### 1순위: Named Tunnel (프로덕션용)
- 영구 URL
- 무료
- 안정적
- **5분 설정으로 영구 해결**

### 2순위: 샌드박스 Ollama (간단)
- 터널 불필요
- 설정 없음
- 느리지만 작동함
- **10분 설치로 독립 실행**

### 3순위: DB 전용 모드 (현재)
- Ollama 없이 사용
- 153개 항목 즉시 응답
- 수동 학습으로 확장
- **이미 작동 중**

---

## 💡 내 추천: Named Tunnel

**이유:**
1. 한 번 설정하면 영구 URL
2. 터널 재시작해도 URL 불변
3. 무료
4. 노트북 GPU 활용 가능
5. 프로덕션 환경 적합

**설정 시간:** 5분
**유지보수:** 0분

---

## 🚀 빠른 시작 가이드

### Named Tunnel 설정 (Windows):

```cmd
REM 1. 로그인 (브라우저 열림, 1회만)
cloudflared tunnel login

REM 2. 터널 생성
cloudflared tunnel create ollama-stable

REM 3. 설정 파일 위치 확인
echo %USERPROFILE%\.cloudflared

REM 4. config.yml 수동 생성 (메모장으로)
REM   C:\Users\wordy\.cloudflared\config.yml

REM 5. 터널 ID 확인 (이전 명령어 출력에서)
cloudflared tunnel list

REM 6. config.yml 내용:
tunnel: <터널-ID>
credentials-file: C:\Users\wordy\.cloudflared\<터널-ID>.json

ingress:
  - hostname: <자동-생성-URL>.trycloudflare.com
    service: http://localhost:11434
  - service: http_status:404

REM 7. 터널 실행 (영구!)
cloudflared tunnel run ollama-stable
```

---

## ⚡ 즉시 실행 가능한 방안

가장 빠른 해결: **샌드박스 Ollama 설치**

```bash
# 복사해서 실행 (5분)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
sleep 5
ollama pull qwen2.5:1.5b
echo "OLLAMA_URL=http://127.0.0.1:11434" > /home/user/webapp/.env
echo "OLLAMA_MODEL=qwen2.5:1.5b" >> /home/user/webapp/.env
cd /home/user/webapp
pkill -f upbit-smart-bot
python3 upbit-smart-bot-v8.0-ULTIMATE.py &
```

**결과:** 더 이상 터널 필요 없음! 🎉

