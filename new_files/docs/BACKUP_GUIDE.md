# 🔒 노트북 서버 백업 가이드

## 📊 백업할 데이터

### 1. 이메이 학습 데이터
**파일**: `upbit_bot.db`  
**크기**: 약 130KB  
**내용**: 
- `emei_knowledge`: 111개 학습 지식
- `emei_conversations`: 모든 대화 기록
- `trade_history`: 매매 내역
- `bot_states`: 봇 상태

### 2. 소스 코드
**파일**: 전체 프로젝트  
**크기**: 약 15MB  
**중요 파일**:
- `upbit-smart-bot-v8.0-ULTIMATE.py` (123KB) - 메인 봇
- `emei_learning.py` (337줄) - 학습 시스템
- `init_emei_knowledge.py` - 기본 지식
- `restore_all_learning_data.py` - 데이터 복구
- `templates/dashboard-ultimate-v3-with-emei.html` - UI

---

## 🔧 백업 방법

### 방법 1: 전체 프로젝트 아카이브
```bash
# 1. 프로젝트 디렉토리로 이동
cd /home/user/webapp

# 2. 전체 압축 (Git 제외)
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    -czf emei_backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# 3. 백업 파일을 노트북으로 복사
# 방법 A: SCP (노트북에서 실행)
scp user@sandbox:/home/user/webapp/emei_backup_*.tar.gz ~/backups/

# 방법 B: HTTP 서버 (샌드박스에서)
python3 -m http.server 8000
# 브라우저에서 다운로드: http://sandbox-url:8000/

# 방법 C: rsync (노트북에서)
rsync -avz user@sandbox:/home/user/webapp/ ~/backups/emei_project/
```

### 방법 2: DB만 백업
```bash
# 1. DB 파일 복사
cp /home/user/webapp/upbit_bot.db /tmp/upbit_bot_backup_$(date +%Y%m%d).db

# 2. 노트북으로 전송 (위와 동일)
```

### 방법 3: Git 저장소 클론 (추천)
```bash
# 노트북에서 실행
git clone https://github.com/wordycow/so.t-leader-choice.git
cd so.t-leader-choice

# 최신 상태로 유지
git pull origin main
```

---

## 📦 복구 방법

### 1. 전체 복원
```bash
# 1. 백업 파일 압축 해제
tar -xzf emei_backup_20260218_021325.tar.gz -C /home/user/webapp/

# 2. 의존성 설치
cd /home/user/webapp
pip install -r requirements.txt

# 3. 서버 시작
python3 upbit-smart-bot-v8.0-ULTIMATE.py
```

### 2. DB만 복원
```bash
# 백업 DB를 현재 DB로 교체
cp upbit_bot_backup_20260218.db /home/user/webapp/upbit_bot.db
```

### 3. Git에서 복원
```bash
# 1. 저장소 클론
git clone https://github.com/wordycow/so.t-leader-choice.git

# 2. 특정 커밋으로 복원
git checkout aea3ed6  # 최신 커밋

# 3. 설정 및 실행
cp .env.example .env
# .env 파일 편집 (API 키 등)
python3 upbit-smart-bot-v8.0-ULTIMATE.py
```

---

## 🔐 중요 데이터 백업 체크리스트

### 매일 백업
- [ ] `upbit_bot.db` (학습 데이터 + 매매 내역)
- [ ] Git 커밋 & 푸시

### 매주 백업
- [ ] 전체 프로젝트 아카이브
- [ ] DB 덤프 (SQL 형식)
  ```bash
  sqlite3 upbit_bot.db .dump > upbit_bot_dump.sql
  ```

### 매달 백업
- [ ] 외부 저장소 (Google Drive, Dropbox 등)
- [ ] 오프라인 백업 (USB 드라이브)

---

## 🌐 노트북 서버 설정

### 1. Ollama 로컬 AI 서버
```bash
# Ollama 설치 (노트북에서)
curl -fsSL https://ollama.com/install.sh | sh

# 모델 다운로드
ollama pull qwen2.5:7b

# 서버 시작
ollama serve

# Cloudflare Tunnel 설정
cloudflared tunnel --url http://localhost:11434
# 생성된 URL을 emei_learning.py에 설정
```

### 2. 노트북 → 샌드박스 동기화
```bash
# rsync로 자동 동기화 (노트북에서)
while true; do
    rsync -avz ~/backups/emei_project/ user@sandbox:/home/user/webapp/
    sleep 3600  # 1시간마다
done
```

---

## 📊 백업 자동화 스크립트

```bash
#!/bin/bash
# backup_emei.sh - 자동 백업 스크립트

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/user/backups"
PROJECT_DIR="/home/user/webapp"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# DB 백업
cp $PROJECT_DIR/upbit_bot.db $BACKUP_DIR/upbit_bot_$DATE.db

# 전체 프로젝트 백업 (주 1회)
if [ $(date +%u) -eq 1 ]; then  # 월요일
    tar --exclude='.git' -czf $BACKUP_DIR/emei_full_$DATE.tar.gz -C $PROJECT_DIR .
fi

# 오래된 백업 정리 (30일 이상)
find $BACKUP_DIR -name "upbit_bot_*.db" -mtime +30 -delete

echo "✅ 백업 완료: $DATE"
```

**Cron 설정 (매일 새벽 3시)**:
```bash
crontab -e
# 추가:
0 3 * * * /home/user/backup_emei.sh
```

---

## 🔄 최신 커밋 정보

**커밋 해시**: `aea3ed6`  
**날짜**: 2026-02-18 02:14  
**변경사항**:
- 봇 매매 조건 극단적 완화
- 모든 학습 데이터 복구 (111개)
- 실제 매수/매도 활성화

**복원 명령**:
```bash
git fetch origin
git checkout aea3ed6
```

---

**백업 완료 시간**: 2026-02-18 02:15 (UTC)  
**다음 백업 예정**: 매일 자동  
**저장 위치**: GitHub + 노트북 로컬
