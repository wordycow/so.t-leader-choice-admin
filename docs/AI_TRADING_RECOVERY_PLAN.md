# 🔄 AI Trading Bot Recovery Plan (Port 5000)

> **Current Status**: AI Trading Bot (port 5000) is currently **INACTIVE**  
> **Goal**: Restore trading bot functionality without forced code changes  
> **Version Reference**: V8.0-ULTIMATE (baseline)

---

## 📋 Table of Contents

1. [Current Situation](#current-situation)
2. [Recovery Checklist](#recovery-checklist)
3. [Required Processes & Files](#required-processes--files)
4. [Port 5000 Configuration](#port-5000-configuration)
5. [Cloudflare Ingress Changes](#cloudflare-ingress-changes)
6. [Status Check from Port 5001](#status-check-from-port-5001)
7. [Failure Categories & Solutions](#failure-categories--solutions)
8. [Testing & Validation](#testing--validation)

---

## 🔍 Current Situation

### Status Summary
- **API Server (5001)**: ✅ Running
- **Trading Bot (5000)**: ❌ Inactive
- **Cloudflare Route**: ai_trading.thetheunique.com → 5001 (temporary)

### Why Port 5000 is Down
1. Trading bot file exists but not started by default
2. Focus on stabilizing port 5001 (Lee May Training Center)
3. Trading strategy under optimization (V8.0-LEARNING)
4. Manual intervention required for safety

### Impact
- External trading dashboard (ai_trading.thetheunique.com) shows port 5001 content
- No active automated trading
- Historical data and DB preserved
- No loss of configuration or strategies

---

## ✅ Recovery Checklist

### Pre-Recovery Verification
- [ ] Confirm Upbit API keys are valid (not expired)
- [ ] Check upbit_bot.db integrity
- [ ] Verify Python dependencies installed
- [ ] Ensure port 5000 is not in use
- [ ] Review recent trading logs for anomalies
- [ ] Backup current DB: `copy upbit_bot.db upbit_bot.db.backup`

### Step-by-Step Recovery
- [ ] **Step 1**: Verify required files exist
- [ ] **Step 2**: Test bot startup manually
- [ ] **Step 3**: Update ops/02_BOTS_START.bat
- [ ] **Step 4**: Update Cloudflare config.yml
- [ ] **Step 5**: Restart Cloudflare tunnel
- [ ] **Step 6**: Verify external access
- [ ] **Step 7**: Monitor for 24 hours

### Post-Recovery Validation
- [ ] Port 5000 accessible locally and externally
- [ ] Dashboard displays real trading data
- [ ] API endpoints respond correctly
- [ ] No port conflicts or crashes
- [ ] Trading strategies execute as expected

---

## 📁 Required Processes & Files

### Core File (V8.0 Baseline)
```
C:\leemay_project\
└─ upbit-smart-bot-v8.0-ULTIMATE.py    # Main trading bot
```

**File Verification**:
```batch
cd C:\leemay_project
if exist upbit-smart-bot-v8.0-ULTIMATE.py (
    echo [OK] Trading bot file found
    python upbit-smart-bot-v8.0-ULTIMATE.py --version  # if supported
) else (
    echo [ERROR] Trading bot file missing
    git pull origin main
)
```

### Database Files
```
C:\leemay_project\
├─ upbit_bot.db              # Trading history, balances, strategies
└─ data\
   └─ sim_trading.db          # Sim trading (separate, not used by real bot)
```

**DB Integrity Check**:
```batch
# Windows (using sqlite3.exe)
sqlite3 upbit_bot.db "SELECT COUNT(*) FROM trades;"
sqlite3 upbit_bot.db "SELECT COUNT(*) FROM balances;"

# Or Python
python -c "import sqlite3; conn=sqlite3.connect('upbit_bot.db'); print('Tables:', [r[0] for r in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')]); conn.close()"
```

### Dependencies
```
requirements.txt:
  - flask>=2.3.0
  - flask-cors>=4.0.0
  - requests>=2.31.0
  - psutil>=5.9.0
  - pyupbit>=0.2.0         # Upbit API
  - pandas>=1.5.0          # Data analysis
  - numpy>=1.23.0          # Numeric computing
  - python-dotenv>=1.0.0   # Environment variables
```

**Install Command**:
```batch
cd C:\leemay_project
pip install -r requirements.txt
```

### Environment Variables (Optional)
```
UPBIT_ACCESS_KEY=<your_key>
UPBIT_SECRET_KEY=<your_secret>
BOT_MODE=real               # or 'sim' for testing
BOT_PORT=5000
```

**Set in Windows**:
```batch
set UPBIT_ACCESS_KEY=your_key
set UPBIT_SECRET_KEY=your_secret
```

Or create `.env` file:
```
UPBIT_ACCESS_KEY=your_key
UPBIT_SECRET_KEY=your_secret
BOT_MODE=real
BOT_PORT=5000
```

---

## 🔌 Port 5000 Configuration

### Manual Bot Startup (Testing)

**Step 1: Test Locally**
```batch
cd C:\leemay_project
python upbit-smart-bot-v8.0-ULTIMATE.py
```

**Expected Output**:
```
🚀 Upbit Smart Bot v8.0 ULTIMATE
📊 Initializing strategies...
🔗 Connecting to Upbit API...
✅ Bot running on http://localhost:5000
Press Ctrl+C to stop...
```

**Verification**:
```batch
# Check process
tasklist | findstr python

# Check port
netstat -ano | findstr :5000

# Test HTTP
curl http://localhost:5000/health
# Expected: {"status": "ok", "version": "8.0"}
```

**Step 2: Background Startup**
```batch
# Start in background (recommended)
start "upbit-bot" /MIN python upbit-smart-bot-v8.0-ULTIMATE.py

# Verify after 5 seconds
timeout /t 5 /nobreak >NUL
curl http://localhost:5000/health
```

### Automated Startup via ops/02_BOTS_START.bat

**Current State** (ops/02_BOTS_START.bat):
```batch
REM AI Trading Bot (포트 5000) - 현재 비활성
echo [WARN] Trading Bot 파일 존재하지만 현재 비활성 상태
```

**Updated State** (after recovery):
```batch
REM ============================================================
REM 1. AI Trading Bot (포트 5000) - 활성화
REM ============================================================
echo [1/2] AI Trading Bot 시작 중...
echo 파일: upbit-smart-bot-v8.0-ULTIMATE.py
echo 포트: 5000
echo.

if exist "upbit-smart-bot-v8.0-ULTIMATE.py" (
    REM 이미 실행 중인지 확인
    tasklist /FI "WINDOWTITLE eq upbit-bot*" 2>NUL | find /I "python.exe" >NUL
    if %ERRORLEVEL% EQU 0 (
        echo [WARN] Trading Bot이 이미 실행 중입니다
    ) else (
        REM 백그라운드 시작
        start "upbit-bot" /MIN python upbit-smart-bot-v8.0-ULTIMATE.py
        timeout /t 5 /nobreak >NUL
        
        REM 시작 확인
        netstat -an | find ":5000" | find "LISTENING" >NUL
        if %ERRORLEVEL% EQU 0 (
            echo [OK] Trading Bot 시작 완료
            echo      로컬: http://localhost:5000
            echo      외부: https://ai_trading.thetheunique.com
        ) else (
            echo [ERROR] Trading Bot 시작 실패
            echo         로그 확인: logs\trading_bot.log
        )
    )
) else (
    echo [ERROR] Trading Bot 파일 없음
)
echo.
```

---

## ☁️ Cloudflare Ingress Changes

### Current Configuration (config.yml)
```yaml
tunnel: <your-tunnel-id>
credentials-file: C:\leemay_project\.cloudflared\<tunnel-id>.json

ingress:
  # Lee May Control Center
  - hostname: leemay.thetheunique.com
    service: http://localhost:5001
  
  # AI Trading Dashboard (현재 5001로 임시 라우팅)
  - hostname: ai_trading.thetheunique.com
    service: http://localhost:5001
  
  # Default 404
  - service: http_status:404
```

### Updated Configuration (after port 5000 recovery)
```yaml
tunnel: <your-tunnel-id>
credentials-file: C:\leemay_project\.cloudflared\<tunnel-id>.json

ingress:
  # Lee May Control Center
  - hostname: leemay.thetheunique.com
    service: http://localhost:5001
  
  # AI Trading Dashboard (복구: 5000으로 변경)
  - hostname: ai_trading.thetheunique.com
    service: http://localhost:5000
  
  # Default 404
  - service: http_status:404
```

### Apply Changes

**Step 1: Validate Configuration**
```batch
cd C:\leemay_project
cloudflared tunnel ingress validate
```

**Expected Output**:
```
Validating rules from C:\leemay_project\config.yml
OK
```

**Step 2: Restart Cloudflare Tunnel**
```batch
# Stop existing tunnel
taskkill /FI "IMAGENAME eq cloudflared.exe" /F

# Wait 2 seconds
timeout /t 2 /nobreak >NUL

# Start with new config
start "cloudflared" /MIN cloudflared tunnel --config config.yml run

# Verify
timeout /t 5 /nobreak >NUL
tasklist | findstr cloudflared
```

**Step 3: Test External Access**
```batch
# Test from external network or use online tools
curl https://ai_trading.thetheunique.com/health

# Expected:
# {"status": "ok", "version": "8.0"}
```

---

## 📡 Status Check from Port 5001

### API Endpoint Integration

The API Server (5001) already has endpoints to monitor port 5000:

**GET /api/ops/status** (existing):
```bash
curl http://localhost:5001/api/ops/status
```

**Response** (when port 5000 active):
```json
{
  "success": true,
  "status": {
    "timestamp": "2026-02-20T12:00:00",
    "control": {
      "api_server": true,
      "cloudflared": true,
      "ollama": true
    },
    "bots": {
      "trading_bot": true,        // ← Should be true after recovery
      "youtube_learner": false
    },
    "ports": {
      "5001": true,
      "5000": true,                // ← Should be true after recovery
      "11434": false
    },
    "overall": "OK"
  }
}
```

### Web Dashboard Integration

**URL**: http://localhost:5001

**Expected Changes After Recovery**:
1. Bot status badge: "STOPPED" → "RUNNING"
2. Port 5000 indicator: Red → Green
3. Trading bot metrics appear in Live Telemetry panel

---

## 🚨 Failure Categories & Solutions

### Category 1: Port Conflict (5000)

**Symptoms**:
- Error: "Address already in use"
- Bot crashes immediately after start
- `netstat -ano | findstr :5000` shows existing process

**Solution**:
```batch
# Find process using port 5000
netstat -ano | findstr :5000
# Output: TCP 0.0.0.0:5000 ... LISTENING 1234

# Kill process
taskkill /PID 1234 /F

# Restart bot
python upbit-smart-bot-v8.0-ULTIMATE.py
```

---

### Category 2: Missing API Keys

**Symptoms**:
- Error: "Invalid API key"
- Bot starts but can't fetch balance
- Upbit API returns 401 Unauthorized

**Solution**:
```batch
# Check environment variables
echo %UPBIT_ACCESS_KEY%
echo %UPBIT_SECRET_KEY%

# If empty, set them
set UPBIT_ACCESS_KEY=your_key
set UPBIT_SECRET_KEY=your_secret

# Or create .env file (recommended)
# See "Environment Variables" section above
```

**Verify Keys**:
```python
# test_upbit_keys.py
import pyupbit

access = "YOUR_ACCESS_KEY"
secret = "YOUR_SECRET_KEY"
upbit = pyupbit.Upbit(access, secret)

try:
    balance = upbit.get_balance("KRW")
    print(f"✅ API Keys valid. Balance: {balance} KRW")
except Exception as e:
    print(f"❌ API Keys invalid: {str(e)}")
```

---

### Category 3: Database Corruption

**Symptoms**:
- Error: "database disk image is malformed"
- Bot crashes during DB query
- Trades not saved

**Solution**:
```batch
# Backup current DB
copy upbit_bot.db upbit_bot.db.backup

# Check integrity (sqlite3.exe required)
sqlite3 upbit_bot.db "PRAGMA integrity_check;"
# Expected: "ok"

# If corrupted, try recovery
sqlite3 upbit_bot.db ".recover" | sqlite3 upbit_bot_recovered.db
move upbit_bot.db upbit_bot.db.corrupted
move upbit_bot_recovered.db upbit_bot.db

# Restart bot
python upbit-smart-bot-v8.0-ULTIMATE.py
```

---

### Category 4: Dependency Issues

**Symptoms**:
- Error: "No module named 'pyupbit'"
- Import errors on startup
- Version compatibility warnings

**Solution**:
```batch
cd C:\leemay_project

# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Or specific package
pip install pyupbit --upgrade

# Verify installation
pip list | findstr pyupbit
# Expected: pyupbit 0.2.x
```

---

### Category 5: Firewall/Network Issues

**Symptoms**:
- Bot starts but can't connect to Upbit API
- External access fails (ai_trading.thetheunique.com)
- Timeout errors

**Solution**:
```batch
# Check firewall rules
netsh advfirewall firewall show rule name=all | findstr 5000

# Add firewall exception if needed
netsh advfirewall firewall add rule name="Lee May Trading Bot" dir=in action=allow protocol=TCP localport=5000

# Test Upbit API connectivity
curl https://api.upbit.com/v1/market/all
# Expected: JSON list of markets

# Test Cloudflare tunnel
curl https://ai_trading.thetheunique.com/health
```

---

### Category 6: Strategy File Missing/Outdated

**Symptoms**:
- Error: "Strategy 'XYZ' not found"
- Bot starts but no trades executed
- Empty strategy list in dashboard

**Solution**:
```batch
# Check for strategy files (depends on bot implementation)
# V8.0 uses embedded strategies, but verify:

# Review bot source
type upbit-smart-bot-v8.0-ULTIMATE.py | findstr "strategy"

# If external strategy files required:
cd C:\leemay_project
git pull origin main
# Or manually copy from backup
```

---

## ✅ Testing & Validation

### Local Testing (Step-by-Step)

**1. Start Bot Locally**
```batch
cd C:\leemay_project
python upbit-smart-bot-v8.0-ULTIMATE.py
```

**2. Test Health Endpoint**
```batch
curl http://localhost:5000/health
# Expected: {"status": "ok", "version": "8.0"}
```

**3. Test Dashboard**
```
Browser: http://localhost:5000
# Should see: Trading dashboard with charts, balances, strategies
```

**4. Test API Endpoints** (if applicable)
```bash
# Get balance
curl http://localhost:5000/api/balance

# Get strategies
curl http://localhost:5000/api/strategies

# Get recent trades
curl http://localhost:5000/api/trades?limit=10
```

---

### External Testing (Cloudflare)

**1. Verify Cloudflare Tunnel**
```batch
tasklist | findstr cloudflared
# Expected: cloudflared.exe running
```

**2. Test External URL**
```bash
# From external network or online tool:
curl https://ai_trading.thetheunique.com/health
# Expected: {"status": "ok", "version": "8.0"}
```

**3. Browser Test**
```
URL: https://ai_trading.thetheunique.com
# Should see: Trading dashboard (same as localhost:5000)
```

---

### Integration Testing (5001 ↔ 5000)

**1. Check from Control Center**
```bash
curl http://localhost:5001/api/ops/status
# Verify: bots.trading_bot = true, ports.5000 = true
```

**2. Web Dashboard Check**
```
URL: http://localhost:5001
# Verify: Bot status shows "RUNNING", port 5000 green
```

**3. Cross-Reference Data**
```bash
# From 5001: Get bot status
curl http://localhost:5001/api/bots/status

# From 5000: Get bot health
curl http://localhost:5000/health

# Both should report consistent states
```

---

### 24-Hour Monitoring Plan

**Hour 0 (Startup)**:
- [ ] Verify bot starts without errors
- [ ] Check initial balance/positions
- [ ] Confirm dashboard accessible

**Hour 1-6 (Early Monitoring)**:
- [ ] Check every hour for crashes
- [ ] Verify trades execute if signals triggered
- [ ] Monitor CPU/memory usage (< 30%)

**Hour 6-12 (Stabilization)**:
- [ ] Check every 2 hours
- [ ] Review trade logs for anomalies
- [ ] Verify external access stable

**Hour 12-24 (Validation)**:
- [ ] Check every 4 hours
- [ ] Calculate P&L accuracy
- [ ] Confirm no memory leaks
- [ ] Review full day logs

**Monitoring Commands**:
```batch
# Process status
ops\99_STATUS.bat

# Recent logs (PowerShell)
Get-Content C:\leemay_project\logs\trading_bot.log -Tail 50

# Real-time monitoring
# Open http://localhost:5000 in browser
```

---

## 📊 Success Metrics

After recovery, the following should be true:

- [x] Port 5000 listening and stable
- [x] Bot process running continuously (no crashes)
- [x] Dashboard accessible locally and externally
- [x] Trades execute according to strategies
- [x] Logs show no critical errors
- [x] CPU < 40%, Memory < 2GB
- [x] External URL responds < 2s
- [x] No port conflicts or firewall blocks

---

## 🔄 Rollback Plan

If recovery fails and causes issues:

**Step 1: Stop Trading Bot**
```batch
ops\03_BOTS_STOP.bat
```

**Step 2: Revert Cloudflare Config**
```yaml
# config.yml
ingress:
  - hostname: ai_trading.thetheunique.com
    service: http://localhost:5001  # Back to 5001
```

**Step 3: Restart Cloudflare**
```batch
taskkill /FI "IMAGENAME eq cloudflared.exe" /F
timeout /t 2 /nobreak >NUL
start "cloudflared" /MIN cloudflared tunnel --config config.yml run
```

**Step 4: Restore DB Backup** (if corrupted)
```batch
copy upbit_bot.db.backup upbit_bot.db /Y
```

**Step 5: Document Issues**
- Record error messages
- Save logs: `copy logs\trading_bot.log logs\trading_bot_failed.log`
- Report to development team

---

## 📚 Related Documents

- [RUNBOOK.md](./RUNBOOK.md) - System operations guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [BOTS_CLASSIFICATION.md](../BOTS_CLASSIFICATION.md) - Bot types and usage

---

## 🆘 Support

**Repository**: https://github.com/wordycow/so.t-leader-choice  
**Maintainer**: wordycow  
**Control Center**: https://leemay.thetheunique.com

---

**Last Updated**: 2026-02-20  
**Status**: Trading Bot INACTIVE (Recovery Plan Ready)  
**Version**: 1.0
