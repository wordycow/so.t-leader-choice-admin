# 🧪 API Testing Guide - Lee May Control Center

> **Purpose**: Test all OPS API endpoints with curl commands  
> **Prerequisites**: Control Center running on port 5001, admin token set

---

## 📋 Table of Contents

1. [Setup & Authentication](#setup--authentication)
2. [OPS API Endpoints](#ops-api-endpoints)
3. [Testing Scenarios](#testing-scenarios)
4. [Expected Responses](#expected-responses)
5. [Troubleshooting](#troubleshooting)

---

## 🔑 Setup & Authentication

### Environment Variables (Windows)
```batch
REM Set admin token (required for POST endpoints)
set ADMIN_TOKEN=your_secret_token_here

REM Optional: Set secret key for session auth
set SECRET_KEY=your_secret_key_here
```

### Environment Variables (Linux/Mac)
```bash
export ADMIN_TOKEN=your_secret_token_here
export SECRET_KEY=your_secret_key_here
```

### Admin Token Usage
All `POST /api/ops/*` endpoints require admin authentication:
- **Header Method**: `X-ADMIN-TOKEN: <your_token>`
- **Session Method**: Login first via `POST /api/auth/login`

**For testing**, we'll use the header method (simpler):
```bash
# Windows (cmd)
set TOKEN=your_admin_token_here

# Linux/Mac (bash)
export TOKEN=your_admin_token_here
```

---

## 🌐 OPS API Endpoints

### 1. POST /api/ops/control/start
**Purpose**: Start CONTROL services (API Server, Cloudflare Tunnel)  
**Auth**: Required  
**Script**: `ops\01_CONTROL_START.bat`

#### Test Command (Windows)
```batch
curl -X POST http://localhost:5001/api/ops/control/start ^
  -H "X-ADMIN-TOKEN: %TOKEN%" ^
  -H "Content-Type: application/json"
```

#### Test Command (Linux/Mac)
```bash
curl -X POST http://localhost:5001/api/ops/control/start \
  -H "X-ADMIN-TOKEN: $TOKEN" \
  -H "Content-Type: application/json"
```

#### Expected Response
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "========================================\nCONTROL START 완료\n...",
  "stderr": ""
}
```

#### Error Response (No Token)
```json
{
  "error": "Unauthorized",
  "message": "Admin token required"
}
```

---

### 2. POST /api/ops/bots/start
**Purpose**: Start BOTS services (Trading Bot, Learning Bots)  
**Auth**: Required  
**Script**: `ops\02_BOTS_START.bat`

#### Test Command (Windows)
```batch
curl -X POST http://localhost:5001/api/ops/bots/start ^
  -H "X-ADMIN-TOKEN: %TOKEN%" ^
  -H "Content-Type: application/json"
```

#### Test Command (Linux/Mac)
```bash
curl -X POST http://localhost:5001/api/ops/bots/start \
  -H "X-ADMIN-TOKEN: $TOKEN" \
  -H "Content-Type: application/json"
```

#### Expected Response (Current State - No Auto-Start)
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "========================================\nBOTS START 완료\n\n현재 자동 시작되는 봇: 없음\n...",
  "stderr": ""
}
```

---

### 3. POST /api/ops/bots/stop
**Purpose**: Stop BOTS services (CONTROL remains running)  
**Auth**: Required  
**Script**: `ops\03_BOTS_STOP.bat`

#### Test Command (Windows)
```batch
curl -X POST http://localhost:5001/api/ops/bots/stop ^
  -H "X-ADMIN-TOKEN: %TOKEN%" ^
  -H "Content-Type: application/json"
```

#### Test Command (Linux/Mac)
```bash
curl -X POST http://localhost:5001/api/ops/bots/stop \
  -H "X-ADMIN-TOKEN: $TOKEN" \
  -H "Content-Type: application/json"
```

#### Expected Response
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "========================================\nBOTS STOP 완료\n\n종료된 봇: Trading Bot, Learning Bots\n유지된 서비스: API Server (5001), Cloudflare Tunnel\n...",
  "stderr": ""
}
```

---

### 4. GET /api/ops/status
**Purpose**: Get comprehensive system status  
**Auth**: Not required (read-only)  
**Script**: `ops\99_STATUS.bat`

#### Test Command (Windows)
```batch
curl http://localhost:5001/api/ops/status
```

#### Test Command (Linux/Mac)
```bash
curl http://localhost:5001/api/ops/status
```

#### Expected Response (All Services Running)
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
      "trading_bot": false,
      "youtube_learner": false
    },
    "ports": {
      "5001": true,
      "5000": false,
      "11434": false
    },
    "overall": "OK"
  },
  "raw_output": "[CONTROL SERVICES]\n...(first 1000 chars)"
}
```

#### Expected Response (CONTROL Down)
```json
{
  "success": true,
  "status": {
    "timestamp": "2026-02-20T12:00:00",
    "control": {
      "api_server": false,
      "cloudflared": false,
      "ollama": true
    },
    "bots": {
      "trading_bot": false,
      "youtube_learner": false
    },
    "ports": {
      "5001": false,
      "5000": false,
      "11434": false
    },
    "overall": "FAIL"
  },
  "raw_output": "..."
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Fresh System Startup

**Goal**: Start CONTROL services from scratch

**Steps**:
```batch
REM 1. Check initial status
curl http://localhost:5001/api/ops/status

REM 2. Start CONTROL services
curl -X POST http://localhost:5001/api/ops/control/start ^
  -H "X-ADMIN-TOKEN: %TOKEN%"

REM 3. Wait 10 seconds
timeout /t 10 /nobreak >NUL

REM 4. Verify status
curl http://localhost:5001/api/ops/status
```

**Expected Results**:
1. Initial status: `overall: "FAIL"` (no services running)
2. Start command: `success: true, exit_code: 0`
3. Final status: `overall: "OK"`, `api_server: true`, `cloudflared: true`

---

### Scenario 2: BOTS Lifecycle

**Goal**: Start and stop BOTS without affecting CONTROL

**Steps**:
```batch
REM 1. Check initial BOTS status
curl http://localhost:5001/api/ops/status

REM 2. Start BOTS (currently just displays info)
curl -X POST http://localhost:5001/api/ops/bots/start ^
  -H "X-ADMIN-TOKEN: %TOKEN%"

REM 3. Stop BOTS
curl -X POST http://localhost:5001/api/ops/bots/stop ^
  -H "X-ADMIN-TOKEN: %TOKEN%"

REM 4. Verify CONTROL still running
curl http://localhost:5001/api/ops/status
```

**Expected Results**:
1. Initial: `trading_bot: false`, `youtube_learner: false`
2. Start: `success: true` (but bots don't auto-start currently)
3. Stop: `success: true`
4. Final: `control.api_server: true` (CONTROL unaffected)

---

### Scenario 3: Status Monitoring

**Goal**: Continuously monitor system health

**PowerShell Script** (Windows):
```powershell
# monitor_status.ps1
while ($true) {
    Clear-Host
    Write-Host "=== Lee May Status Monitor ===" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date)" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/ops/status"
    $status = $response.status
    
    Write-Host "CONTROL:" -ForegroundColor Green
    Write-Host "  API Server: $($status.control.api_server)"
    Write-Host "  Cloudflared: $($status.control.cloudflared)"
    Write-Host "  Ollama: $($status.control.ollama)"
    Write-Host ""
    
    Write-Host "BOTS:" -ForegroundColor Yellow
    Write-Host "  Trading Bot: $($status.bots.trading_bot)"
    Write-Host "  YouTube Learner: $($status.bots.youtube_learner)"
    Write-Host ""
    
    Write-Host "PORTS:" -ForegroundColor Magenta
    Write-Host "  5001: $($status.ports.'5001')"
    Write-Host "  5000: $($status.ports.'5000')"
    Write-Host ""
    
    $overallColor = if ($status.overall -eq "OK") { "Green" } else { "Red" }
    Write-Host "OVERALL: $($status.overall)" -ForegroundColor $overallColor
    
    Start-Sleep -Seconds 5
}
```

**Bash Script** (Linux/Mac):
```bash
#!/bin/bash
# monitor_status.sh

while true; do
    clear
    echo "=== Lee May Status Monitor ==="
    echo "Time: $(date)"
    echo ""
    
    STATUS=$(curl -s http://localhost:5001/api/ops/status)
    
    echo "CONTROL:"
    echo "  API Server: $(echo $STATUS | jq -r '.status.control.api_server')"
    echo "  Cloudflared: $(echo $STATUS | jq -r '.status.control.cloudflared')"
    echo "  Ollama: $(echo $STATUS | jq -r '.status.control.ollama')"
    echo ""
    
    echo "BOTS:"
    echo "  Trading Bot: $(echo $STATUS | jq -r '.status.bots.trading_bot')"
    echo "  YouTube Learner: $(echo $STATUS | jq -r '.status.bots.youtube_learner')"
    echo ""
    
    echo "PORTS:"
    echo "  5001: $(echo $STATUS | jq -r '.status.ports."5001"')"
    echo "  5000: $(echo $STATUS | jq -r '.status.ports."5000"')"
    echo ""
    
    echo "OVERALL: $(echo $STATUS | jq -r '.status.overall')"
    
    sleep 5
done
```

**Run**:
```batch
REM Windows
powershell -ExecutionPolicy Bypass -File monitor_status.ps1

REM Linux/Mac
chmod +x monitor_status.sh
./monitor_status.sh
```

---

### Scenario 4: Error Handling

**Goal**: Test API behavior on errors

#### Test 1: Missing Admin Token
```bash
curl -X POST http://localhost:5001/api/ops/control/start \
  -H "Content-Type: application/json"
```

**Expected**: `401 Unauthorized` or `{"error": "Unauthorized"}`

#### Test 2: Invalid Admin Token
```bash
curl -X POST http://localhost:5001/api/ops/control/start \
  -H "X-ADMIN-TOKEN: invalid_token_123" \
  -H "Content-Type: application/json"
```

**Expected**: `401 Unauthorized` or `{"error": "Invalid token"}`

#### Test 3: Script Execution Failure (Simulated)
If script returns non-zero exit code:
```json
{
  "success": false,
  "exit_code": 1,
  "stdout": "...",
  "stderr": "ERROR: ..."
}
```

#### Test 4: Timeout (60s limit)
If script takes > 60s:
```json
{
  "success": false,
  "error": "Timeout (60s)"
}
```

---

## 📊 Expected Responses

### Success Response Format
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "Script output here...",
  "stderr": ""
}
```

### Error Response Format (Script Failed)
```json
{
  "success": false,
  "exit_code": 1,
  "stdout": "Partial output...",
  "stderr": "Error message..."
}
```

### Error Response Format (Auth Failed)
```json
{
  "error": "Unauthorized",
  "message": "Admin token required"
}
```

### Status Response Format
```json
{
  "success": true,
  "status": {
    "timestamp": "ISO-8601 datetime",
    "control": {
      "api_server": boolean,
      "cloudflared": boolean,
      "ollama": boolean
    },
    "bots": {
      "trading_bot": boolean,
      "youtube_learner": boolean
    },
    "ports": {
      "5001": boolean,
      "5000": boolean,
      "11434": boolean
    },
    "overall": "OK" | "WARN" | "FAIL"
  },
  "raw_output": "First 1000 chars of script output"
}
```

---

## 🔧 Troubleshooting

### Issue 1: Connection Refused

**Error**:
```
curl: (7) Failed to connect to localhost port 5001: Connection refused
```

**Cause**: API Server not running

**Solution**:
```batch
REM Check if server is running
netstat -ano | findstr :5001

REM If not, start manually
cd C:\leemay_project
python api_server.py
```

---

### Issue 2: Unauthorized (No Token)

**Error**:
```json
{"error": "Unauthorized", "message": "Admin token required"}
```

**Cause**: Missing or invalid `X-ADMIN-TOKEN` header

**Solution**:
```batch
REM Set environment variable
set ADMIN_TOKEN=your_token_here

REM Check if set
echo %ADMIN_TOKEN%

REM Retry with token
curl -X POST http://localhost:5001/api/ops/control/start ^
  -H "X-ADMIN-TOKEN: %ADMIN_TOKEN%"
```

---

### Issue 3: Script Execution Failed

**Error**:
```json
{
  "success": false,
  "exit_code": 1,
  "stdout": "...",
  "stderr": "ERROR: Python not found"
}
```

**Cause**: Missing dependencies or script errors

**Solution**:
```batch
REM Check logs
type C:\leemay_project\logs\ops_api.log

REM Run script manually to debug
cd C:\leemay_project\ops
01_CONTROL_START.bat
```

---

### Issue 4: Timeout (60s)

**Error**:
```json
{
  "success": false,
  "error": "Timeout (60s)"
}
```

**Cause**: Script took too long (e.g., waiting for user input)

**Solution**:
- Check if script has `pause` commands
- Remove interactive prompts from batch files
- Increase timeout in api_server.py (not recommended)

---

### Issue 5: CORS Error (Browser)

**Error** (in browser console):
```
Access to XMLHttpRequest at 'http://localhost:5001/api/ops/status' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Cause**: Frontend origin not in CORS_ORIGINS

**Solution**:
```batch
REM Add origin to CORS_ORIGINS
set CORS_ORIGINS=http://localhost:5000,http://localhost:3000

REM Restart API server
```

---

## 📝 Logging & Audit

### OPS API Logs
**Path**: `C:\leemay_project\logs\ops_api.log`

**View**:
```batch
REM Windows
type C:\leemay_project\logs\ops_api.log

REM Real-time (PowerShell)
Get-Content C:\leemay_project\logs\ops_api.log -Wait
```

**Sample Log**:
```
[2026-02-20T12:00:00] Executing: C:\leemay_project\ops\01_CONTROL_START.bat
[2026-02-20T12:00:05] Exit code: 0
[2026-02-20T12:00:05] Output: ========================================...
```

### Audit Logs (Admin Actions)
**Endpoint**: `GET /api/admin/audit/list`

**Test**:
```bash
curl http://localhost:5001/api/admin/audit/list?limit=50
```

**Response**:
```json
{
  "success": true,
  "audit_logs": [
    {
      "id": 1,
      "event_type": "OPS_CONTROL_START",
      "event_name": "01_CONTROL_START.bat 실행",
      "user_id": "admin",
      "timestamp": "2026-02-20T12:00:00",
      "detail": "{}"
    }
  ]
}
```

---

## 🚀 Quick Test Suite (All-in-One)

**Windows Batch**:
```batch
@echo off
REM test_ops_api.bat

echo ========================================
echo Lee May OPS API Test Suite
echo ========================================
echo.

REM Set admin token
set TOKEN=your_token_here

echo [1/4] Testing status endpoint...
curl -s http://localhost:5001/api/ops/status | jq .status.overall
echo.

echo [2/4] Testing control start (requires auth)...
curl -s -X POST http://localhost:5001/api/ops/control/start ^
  -H "X-ADMIN-TOKEN: %TOKEN%" | jq .success
echo.

echo [3/4] Testing bots start (requires auth)...
curl -s -X POST http://localhost:5001/api/ops/bots/start ^
  -H "X-ADMIN-TOKEN: %TOKEN%" | jq .success
echo.

echo [4/4] Testing bots stop (requires auth)...
curl -s -X POST http://localhost:5001/api/ops/bots/stop ^
  -H "X-ADMIN-TOKEN: %TOKEN%" | jq .success
echo.

echo ========================================
echo Tests Complete
echo ========================================
pause
```

**Linux/Mac Bash**:
```bash
#!/bin/bash
# test_ops_api.sh

echo "========================================"
echo "Lee May OPS API Test Suite"
echo "========================================"
echo ""

# Set admin token
export TOKEN=your_token_here

echo "[1/4] Testing status endpoint..."
curl -s http://localhost:5001/api/ops/status | jq .status.overall
echo ""

echo "[2/4] Testing control start (requires auth)..."
curl -s -X POST http://localhost:5001/api/ops/control/start \
  -H "X-ADMIN-TOKEN: $TOKEN" | jq .success
echo ""

echo "[3/4] Testing bots start (requires auth)..."
curl -s -X POST http://localhost:5001/api/ops/bots/start \
  -H "X-ADMIN-TOKEN: $TOKEN" | jq .success
echo ""

echo "[4/4] Testing bots stop (requires auth)..."
curl -s -X POST http://localhost:5001/api/ops/bots/stop \
  -H "X-ADMIN-TOKEN: $TOKEN" | jq .success
echo ""

echo "========================================"
echo "Tests Complete"
echo "========================================"
```

**Run**:
```batch
REM Windows (requires jq: https://stedolan.github.io/jq/)
test_ops_api.bat

REM Linux/Mac
chmod +x test_ops_api.sh
./test_ops_api.sh
```

---

## 📚 Related Documents

- [RUNBOOK.md](./RUNBOOK.md) - Operational procedures
- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Full API reference (if exists)
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture

---

**Last Updated**: 2026-02-20  
**Version**: 1.0
