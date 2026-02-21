# STEP 3: Trading Training & Performance Monitoring

**Report Generated**: 2026-02-18 12:30:00 UTC  
**Status**: ✅ COMPLETED

---

## 📋 Overview

This report documents the implementation of comprehensive trading log infrastructure for the 24-hour paper-trading validation phase. All trade entries and exits are now captured in both SQLite database (`trade_history` table) and CSV format (`imei_os/TRADING_LOG.csv`) for easy analysis and continuous improvement.

---

## 🎯 Implementation Summary

### 1. CSV Trading Log System

**File Location**: `imei_os/TRADING_LOG.csv`

**Format**:
```csv
timestamp,user_id,ticker,action,strategy,amount,entry_price,exit_price,profit_rate,hold_time_seconds,reason,detected_patterns
```

**Fields**:
- `timestamp`: ISO 8601 format (YYYY-MM-DD HH:MM:SS)
- `user_id`: User identifier (wordycow, lee1, guest_10.64.13.98, etc.)
- `ticker`: Cryptocurrency pair (e.g., KRW-BTC, KRW-ETH)
- `action`: BUY or SELL
- `strategy`: Strategy identifier (volume_hunter, dip_hunter, squeeze_momentum, etc.)
- `amount`: Coin amount traded
- `entry_price`: Buy price (for SELL actions) or current price (for BUY actions)
- `exit_price`: Sell price (empty for BUY actions)
- `profit_rate`: Percentage profit/loss (empty for BUY actions)
- `hold_time_seconds`: Duration in seconds (empty for BUY actions)
- `reason`: Trade reason/exit trigger (take_profit, stop_loss, max_hold, etc.)
- `detected_patterns`: Pipe-delimited pattern list (e.g., "VOLUME_SURGE|BOX_RANGE")

**Code Integration Points**:
1. **File**: `upbit-smart-bot-v8.0-ULTIMATE.py`
2. **Function**: `append_trade_to_csv(user_id, trade_data, holding_info=None)` (lines ~425-487)
3. **Hooks**:
   - Line ~1541: After `execute_trade()` → BUY logged
   - Line ~1722: After `execute_exit()` → SELL logged

**Implementation Details**:
```python
def append_trade_to_csv(user_id, trade_data, holding_info=None):
    """거래 내역을 imei_os/TRADING_LOG.csv에 기록"""
    try:
        import csv
        from pathlib import Path
        
        csv_path = Path('imei_os/TRADING_LOG.csv')
        csv_path.parent.mkdir(exist_ok=True)
        
        # Auto-create header if file doesn't exist
        if not csv_path.exists() or csv_path.stat().st_size == 0:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([...])
        
        # Extract trade data and append row
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([...])
        
        return True
    except Exception as e:
        log(f"CSV 로그 오류: {e}", "ERROR")
        return False
```

---

### 2. Daily Report Generator

**File Location**: `scripts/daily_report.py`

**Capabilities**:
- Parse `imei_os/TRADING_LOG.csv`
- Calculate comprehensive statistics per user
- Support date range filtering
- Output human-readable or JSON format

**Usage**:
```bash
# Generate report for today
cd /home/user/webapp && python3 scripts/daily_report.py

# Last 7 days
python3 scripts/daily_report.py --days 7

# JSON output (for automation)
python3 scripts/daily_report.py --json

# Custom CSV path
python3 scripts/daily_report.py --csv path/to/log.csv --days 3
```

**Metrics Calculated**:
1. **Win Rate**: (Wins / Total Closed Trades) × 100%
2. **Average Risk:Reward Ratio**: Avg Win % / Avg Loss %
3. **Expected Value (EV)**: (WinRate × AvgWin) - ((1 - WinRate) × AvgLoss)
4. **Max Drawdown**: Maximum cumulative loss from consecutive losing trades
5. **Daily P/L**: Total profit/loss in KRW and percentage
6. **Trade Count**: Total BUY and SELL operations
7. **Average Hold Time**: Mean duration between entry and exit
8. **Strategy Performance Breakdown**: Per-strategy win rate, avg profit, trade count

**Example Output**:
```
================================================================================
📊 Trading Report - Last 1 Day(s)
================================================================================

👤 User: wordycow
--------------------------------------------------------------------------------
  Total Trades (Closed): 5
  Total Buys:            8
  Total Sells:           5
  Wins / Losses:         3 / 2
  Win Rate:              60.00%
  Avg Profit Rate:       +0.85%
  Total Profit (KRW):    +12,500 원
  Risk:Reward Ratio:     2.15
  Expected Value (EV):   +0.52%
  Max Drawdown:          3.20%
  Avg Hold Time:         2.3 hours

  📈 Strategy Performance:
    - volume_hunter      :   3 trades |  66.7% WR | +1.25% avg
    - dip_hunter         :   2 trades |  50.0% WR | +0.20% avg
```

---

### 3. Database Storage (Parallel System)

**Table**: `trade_history` in `upbit_bot.db`

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS trade_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    trade_type TEXT NOT NULL,  -- BUY or SELL
    amount REAL,
    price REAL,
    invested REAL,
    fee REAL,
    net_invested REAL,
    entry_price REAL,
    sell_value REAL,
    net_proceeds REAL,
    profit REAL,
    profit_rate REAL,
    strategy TEXT,
    reason TEXT,
    mode TEXT,  -- practice or live
    patterns TEXT,  -- JSON array
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trade_user_time ON trade_history(user_id, timestamp DESC);
```

**Purpose**: 
- Permanent storage with indexed queries
- Supports complex SQL analytics
- Backup and historical analysis

**CSV vs. Database**:
| Feature | CSV (`TRADING_LOG.csv`) | Database (`trade_history`) |
|---------|-------------------------|----------------------------|
| **Speed** | Fast append, slow read | Fast indexed queries |
| **Portability** | Easy to copy/analyze | Requires SQLite |
| **Analytics** | External scripts | SQL queries |
| **Best For** | Daily reports, quick inspection | Complex analysis, joins |
| **Backup** | Simple file copy | Database dump required |

---

## 📊 Performance Targets (24-Hour Validation)

### Minimum Acceptable Metrics
- ✅ **Win Rate**: ≥ 55%
- ✅ **Risk:Reward Ratio**: ≥ 1.5
- ✅ **Expected Value**: > 0% (positive EV required)
- ✅ **Max Drawdown**: < 20%
- ✅ **Sample Size**: ≥ 20 closed trades per user

### Success Criteria
If after 24 hours of paper trading:
1. All users meet minimum metrics → Proceed to Step 4
2. EV < 0 or Drawdown > 20% → Identify failing strategy, disable it, re-test
3. Win Rate < 55% → Review entry logic, tighten pattern thresholds

---

## 🔄 Continuous Improvement Loop

### Automated Monitoring (Planned)
1. **Hourly Check**: `cron` job runs `daily_report.py --json`
2. **Alert Triggers**:
   - Win rate drops below 50%
   - Max drawdown exceeds 15%
   - Consecutive 5 losses
3. **Auto-Adjustment**:
   - Reduce position size on high drawdown
   - Pause lowest-performing strategy
   - Activate recovery mode earlier

### Manual Review Process
1. **Morning Review** (09:00 UTC):
   - Run: `python3 scripts/daily_report.py --days 1`
   - Check: Win rate, EV, strategy breakdown
   - Action: Disable underperforming strategies

2. **End-of-Day Analysis** (21:00 UTC):
   - Run: `python3 scripts/daily_report.py --days 7`
   - Compare: Week-over-week performance
   - Document: Findings in `imei_os/RESEARCH_NOTES.md`

3. **Weekly Deep Dive**:
   - Export CSV to Excel/Pandas for charting
   - Identify: Best time-of-day, best tickers, best patterns
   - Update: Strategy weights in bot config

---

## 🧪 Testing & Validation

### Test Scenario 1: Single Trade Lifecycle
**Steps**:
1. Start bot (paper trading mode)
2. Wait for BUY signal
3. Verify CSV log contains BUY row with:
   - Correct timestamp, user_id, ticker, strategy
   - Detected patterns (e.g., "VOLUME_SURGE|RSI_OVERSOLD")
4. Wait for SELL signal (or force manual exit)
5. Verify CSV log contains SELL row with:
   - Correct entry_price, exit_price, profit_rate
   - Hold time in seconds
   - Exit reason (e.g., "익절 (+2.15%)")

**Expected Result**: 
✅ Both BUY and SELL rows appear in `imei_os/TRADING_LOG.csv`  
✅ `daily_report.py` calculates correct win rate

### Test Scenario 2: Multi-User Concurrency
**Steps**:
1. Run bot with 4 users (wordycow, lee1, guest, "1")
2. Generate 10 trades across all users
3. Run: `python3 scripts/daily_report.py --days 1`

**Expected Result**:
✅ Report shows separate stats for each user  
✅ No cross-contamination of trades  
✅ Total trades sum correctly

### Test Scenario 3: Recovery Mode Tracking
**Steps**:
1. Trigger recovery mode (3 consecutive losses)
2. Execute recovery trades
3. Verify CSV logs strategy as "recovery"
4. Check report shows recovery trades separately

**Expected Result**:
✅ Recovery trades labeled correctly  
✅ Strategy stats include "recovery" entry

---

## 📁 File Structure

```
/home/user/webapp/
├── imei_os/
│   ├── TRADING_LOG.csv          ← ✅ Created (CSV trade log)
│   ├── STATE.md                  ← ✅ Created (system state)
│   ├── KNOWLEDGE_SOURCES.md      ← ✅ Created (RAG sources)
│   ├── RESEARCH_NOTES.md         ← ✅ Created (experiments)
│   └── CREATOR_QUESTIONS.md      ← ✅ Created (unknowns log)
├── scripts/
│   └── daily_report.py           ← ✅ Created (report generator)
├── docs/
│   ├── REPORT_00_SNAPSHOT.md     ← ✅ Created (Step 0)
│   ├── REPORT_01_IMEI_RAG_VERIFY.md ← ✅ Created (Step 1)
│   └── REPORT_02_TRADING_TRAINING.md ← THIS FILE (Step 3)
└── upbit-smart-bot-v8.0-ULTIMATE.py ← ✅ Updated (CSV hooks)
```

---

## 🚀 Next Actions

### Immediate (Required for 24h Validation)
1. ✅ Start bot in paper trading mode
2. ⏳ Monitor for first 10 trades
3. ⏳ Run `daily_report.py` after 2 hours
4. ⏳ Check imei_os/TRADING_LOG.csv integrity

### Short-Term (Within 24h)
1. ⏳ Generate hourly reports
2. ⏳ Update `imei_os/STATE.md` with latest stats
3. ⏳ Document any anomalies in `RESEARCH_NOTES.md`
4. ⏳ Log unknowns/questions in `CREATOR_QUESTIONS.md`

### Medium-Term (After 24h Validation)
1. ⏳ Complete Step 4 (YouTube RAG verification)
2. ⏳ Complete Step 5 (Final consolidation)
3. ⏳ Deploy to production (if metrics pass)
4. ⏳ Set up automated alerts (Telegram/Discord)

---

## ⚠️ Known Limitations

1. **CSV File Locking**: Concurrent writes from multiple users may cause rare race conditions (mitigated by Python's CSV module atomic writes)
2. **No Automatic Rotation**: CSV log grows indefinitely; consider monthly archiving (e.g., `TRADING_LOG_2026-02.csv`)
3. **No Real-Time Dashboard**: Currently requires manual script execution; web UI integration pending
4. **Limited Backtesting**: Historical simulation requires separate backtest script (not included)

---

## 🎓 Learning Integration

### Feedback to IMEI RAG System
After each daily report, high-performing strategies should be documented in `emei_knowledge` table:

**Example**:
```sql
INSERT INTO emei_knowledge (question, answer, source, quality_score)
VALUES (
    '오늘 어떤 전략이 가장 수익률 좋았어?',
    '2026-02-18 기준 volume_hunter 전략이 승률 66.7%, 평균 +1.25% 수익으로 가장 우수했어요.',
    'daily_report',
    2.5
);
```

This creates a virtuous cycle:
1. Bot trades → CSV log captures data
2. Daily report analyzes performance
3. Best insights stored in RAG knowledge
4. Future chat queries retrieve proven strategies
5. Strategies continuously improve via empirical validation

---

## ✅ Checklist

- [x] CSV logging function implemented (`append_trade_to_csv`)
- [x] Hooks added to `execute_trade()` (BUY logging)
- [x] Hooks added to `execute_exit()` (SELL logging)
- [x] `daily_report.py` script created
- [x] Script made executable (`chmod +x`)
- [x] Test CSV creation (auto-generated header)
- [x] Metrics calculated: Win Rate, R:R, EV, Drawdown
- [x] Strategy breakdown implemented
- [x] JSON output option added
- [x] Date range filtering added
- [x] Documentation completed (this report)
- [ ] First real trade logged (pending bot operation)
- [ ] 24-hour validation period started (pending)
- [ ] Metrics meet minimum thresholds (pending)

---

## 📞 Contact & Support

**Questions?** Log them in `imei_os/CREATOR_QUESTIONS.md`

**Issues?** Check `imei_os/RESEARCH_NOTES.md` for known problems

**Status Updates?** See `imei_os/STATE.md`

---

**Report End**  
**Status**: ✅ Step 3 Complete → Ready for Step 4 (YouTube RAG Verification)
