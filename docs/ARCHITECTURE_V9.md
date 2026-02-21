# UPBIT BOT v9 - Architecture Specification

**Version**: 9.0.0  
**Date**: 2026-02-18  
**Status**: 🔴 DESIGN PHASE  
**Creator**: Yusong (Final Approved)

---

## 🎯 Core Philosophy

**2-Engine Split Architecture**: Complete separation of signal generation and trade execution to achieve:
- API overload prevention (single 5-min snapshot call)
- Clear signal/execution separation
- Strategy transparency
- Long-term maintainability  
- Real-money safety (double lock gates)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SIGNAL ENGINE                        │
│                 (Local PC - RTX 5070ti)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────┐          │
│  │  5-Minute Snapshot Diff Scorer          │          │
│  │  - Fetch all tickers (300s interval)    │          │
│  │  - Calculate delta_money, delta_volume  │          │
│  │  - Score: 0.5*money + 0.3*price + 0.2*vol │       │
│  │  - Maintain TOP 20 candidates           │          │
│  └─────────────────────────────────────────┘          │
│                      ↓                                  │
│  ┌─────────────────────────────────────────┐          │
│  │  BTC Regime Detector                    │          │
│  │  - BTC 1H/4H trend                      │          │
│  │  - Stablecoin supply delta              │          │
│  │  - BTC dominance delta                  │          │
│  │  → FULL_DOWNTREND flag                  │          │
│  └─────────────────────────────────────────┘          │
│                      ↓                                  │
│  ┌─────────────────────────────────────────┐          │
│  │  Strategy Signal Generators             │          │
│  │  - Ultra Scalp Monitor (1m)             │          │
│  │  - Deep Hunter Monitor (1H)             │          │
│  │  → Structured signals only              │          │
│  └─────────────────────────────────────────┘          │
│                      ↓                                  │
│             WebSocket Emit                              │
└─────────────────────────────────────────────────────────┘
                       ↓
              [WebSocket Channel]
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  EXECUTION ENGINE                       │
│                   (Novita Server)                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│             WebSocket Receive                           │
│                      ↓                                  │
│  ┌─────────────────────────────────────────┐          │
│  │  Signal Validator                       │          │
│  │  - Revalidate regime                    │          │
│  │  - Check capital allocation             │          │
│  │  - Verify survival filters              │          │
│  │  → Accept/Reject decision               │          │
│  └─────────────────────────────────────────┘          │
│                      ↓                                  │
│  ┌─────────────────────────────────────────┐          │
│  │  Trade Executor                         │          │
│  │  - Upbit API calls                      │          │
│  │  - Order placement                      │          │
│  │  - Partial exits (3%, 5%, 7%+)          │          │
│  │  - Time stops (6 min)                   │          │
│  └─────────────────────────────────────────┘          │
│                      ↓                                  │
│  ┌─────────────────────────────────────────┐          │
│  │  Portfolio Manager                      │          │
│  │  - Recovery engine (-20% handling)      │          │
│  │  - BTC stacking (profit → BTC)          │          │
│  │  - Capital allocation tracking          │          │
│  └─────────────────────────────────────────┘          │
│                      ↓                                  │
│  ┌─────────────────────────────────────────┐          │
│  │  Dashboard & Logging                    │          │
│  │  - Single-screen layout                 │          │
│  │  - Strategy performance                 │          │
│  │  - Real-time updates                    │          │
│  └─────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚫 STRICT SEPARATION RULES

### Signal Engine MUST NOT:
- ❌ Execute trades
- ❌ Access API keys
- ❌ Manage capital
- ❌ Place orders
- ❌ Hold position state
- ✅ Only emit structured signals

### Execution Engine MUST NOT:
- ❌ Generate strategy signals
- ❌ Run indicator calculations
- ❌ Monitor tickers continuously
- ✅ Only react to WebSocket signals
- ✅ Only execute validated trades

---

## 📡 WebSocket Communication Protocol

### Signal Payload Schema
```json
{
  "signal_type": "ENTRY" | "EXIT" | "REGIME_CHANGE",
  "strategy_id": "ULTRA_SCALP_V2_1",
  "ticker": "KRW-XXX",
  "confidence": 0.87,
  "snapshot_score": 0.91,
  "btc_regime": "NORMAL" | "FULL_DOWNTREND",
  "indicators": {
    "rsi_14": 18.5,
    "bb_lower": 1250,
    "volume_spike": 3.2
  },
  "timestamp": 1739872340,
  "signal_id": "uuid-v4"
}
```

### Execution Response Schema
```json
{
  "signal_id": "uuid-v4",
  "status": "ACCEPTED" | "REJECTED",
  "reject_reason": "REGIME_INVALID" | "CAP_EXCEEDED" | "SURVIVAL_FAIL",
  "order_id": "upbit-order-123",
  "executed_amount": 150000,
  "executed_price": 1255,
  "timestamp": 1739872342
}
```

---

## 🔍 TOP 20 Candidate Selection (Signal Engine)

### Every 300 Seconds:
1. **Fetch Full Snapshot**: `pyupbit.get_tickers("KRW")`
2. **Calculate Deltas**:
   ```python
   delta_money = current.acc_trade_price - previous.acc_trade_price
   delta_volume = current.acc_trade_volume - previous.acc_trade_volume
   price_change_pct = (current.trade_price - previous.trade_price) / previous.trade_price
   ```

3. **Score Formula**:
   ```python
   score = (
       0.5 * rank(delta_money) +
       0.3 * price_change_pct +
       0.2 * rank(delta_volume)
   )
   ```

4. **Ranking**:
   - Sort by score descending
   - Take TOP 20
   - Log candidate rotation

5. **Exclusions**:
   - Warning-listed coins
   - Delisting risk coins
   - Bottom 5% liquidity
   - BTC/USDT markets (only KRW traded)

6. **WebSocket Subscriptions**:
   - Unsubscribe from dropped tickers
   - Subscribe to new TOP 20 only

---

## 📊 BTC Regime Detection (Signal Engine)

### Inputs:
- BTC 1H trend (SMA 20 vs. SMA 50)
- BTC 4H trend (SMA 20 vs. SMA 50)
- Global stablecoin supply delta (1H change)
- BTC dominance delta (1H change)

### Logic:
```python
if (
    btc_1h_trend == "BEARISH" and
    btc_4h_trend == "BEARISH" and
    (stablecoin_spike > 2% or dominance_spike > 1%)
):
    FULL_DOWNTREND = True
else:
    FULL_DOWNTREND = False
```

### When FULL_DOWNTREND = True:
- ❌ Disable Ultra Scalp
- ❌ Disable Deep Hunter
- ❌ Block new entries
- ✅ Only exits allowed
- 📝 Log regime transition

---

## ⚡ Strategy: Ultra Scalp (1-Minute)

### Entry Conditions:
- 1m close below lower Bollinger (20, 2)
- RSI(14) < 20
- 3 consecutive red candles
- Volume spike > 2x avg
- Ticker in TOP 20
- FULL_DOWNTREND = False

### Capital Rules:
- **Per Trade**: 10% of available capital
- **Max Concurrent**: 2 positions
- **Max Total Allocation**: 20%

### Exit Logic:
1. **+3% Profit**:
   - Sell 30%
   - Move stop-loss to break-even

2. **+5% Profit**:
   - Sell 40% (cumulative 70%)
   - Activate trailing stop 1.5%

3. **+7%+ Profit**:
   - Remaining 30% trailing stop
   - Sell if -1.8% from peak

4. **Time Stop** (6 minutes):
   - If +1% not reached → full exit
   - Log: `TIME_STOP`

### Exit Reasons Logged:
- `PARTIAL_3`: +3% partial exit
- `PARTIAL_5`: +5% partial exit
- `TRAIL_7`: +7% trailing exit
- `TIME_STOP`: 6-min timeout

---

## 🎣 Strategy: Deep Hunter (1-Hour)

### Entry Conditions:
- 1H extreme oversold (RSI < 15)
- Lower Bollinger break (1H)
- NOT during BTC full collapse
- Ticker in TOP 20

### Capital Rules:
- **Start Small**: 5% initial
- **Staged Averaging**: Up to 15% total
- **Final Buy**: Only when drop slowdown detected

### Exit Logic:
- **NO hard -2% stop-loss**
- Recovery-based exit
- Partial exits allowed
- Monitor for reversal signals

---

## 🛡️ Recovery Engine (Execution Engine)

### Trigger:
- Portfolio contains position with -20% unrealized loss

### Actions:
1. **DO NOT auto stop-loss** the -20% position
2. **Sell 10-50%** of least-negative holdings
3. **Reallocate** freed capital only if:
   - Regime is valid
   - New signal confidence > 0.8
4. **Log** recovery action with:
   - Original position ticker
   - Loss percentage
   - Reallocation decision
   - New signal executed (if any)

---

## 💎 BTC Stacking (Execution Engine)

### Rule:
Every realized profit >= 10,000 KRW → **Buy BTC spot**

### Logging:
- Separate BTC accumulation log
- Track total BTC accumulated
- Track average BTC buy price
- Display in dashboard: "BTC Stack: 0.00123 BTC"

---

## 📝 Strategy Registry (Structured JSON)

### Required Fields:
```json
{
  "id": "ULTRA_SCALP_V2_1",
  "display_name": "Ultra Scalp v2.1",
  "stop_loss_pct": -2.0,
  "take_profit_pct": 3.0,
  "trailing_stop_pct": 1.5,
  "entry_indicators": [
    "bb_lower_break",
    "rsi_14_below_20",
    "three_red_candles",
    "volume_spike_2x"
  ],
  "exit_logic": "PARTIAL_EXITS_3_5_7",
  "time_stop": 360,
  "capital_rule": {
    "per_trade_pct": 10,
    "max_concurrent": 2,
    "max_total_pct": 20
  },
  "source": "manual" | "youtube" | "backtest"
}
```

### YouTube Strategy Conversion:
- Parse learned strategies from `emei_knowledge` table
- Extract key parameters (stop%, profit%, indicators)
- Reject if % not defined
- Store in `strategy_registry.json`

---

## 🔐 Safety Gates (Execution Engine)

### Double Lock Required:
1. **ENV Variable**: `ENABLE_REAL_TRADING=true`
2. **Flag File**: `/home/user/webapp/enable_live.flag` must exist

### Hard Limits (Live Phase):
- **Max Exposure**: 100,000 KRW during first live phase
- **Daily Drawdown**: -2% equity drop → auto halt
- **Emergency Stop**: Manual `/api/emergency_stop` endpoint

### Validation Sequence:
```python
def can_execute_real_order():
    if os.getenv('ENABLE_REAL_TRADING') != 'true':
        return False
    if not os.path.exists('/home/user/webapp/enable_live.flag'):
        return False
    if total_exposure > 100_000:
        return False
    if daily_drawdown_pct < -2.0:
        return False
    return True
```

---

## 🖥️ Compact Dashboard (Single-Screen)

### Layout:
```
┌─────────────────────────────────────────────────────┐
│  [Mode: PRACTICE] [Status: RUNNING] [Update: 5s ago]│
├─────────────────────────────────────────────────────┤
│  KPIs:                                              │
│  Total Equity: 1,234,567 KRW  Daily PnL: +12,345   │
│  Cash: 800,000  Invested: 434,567  Positions: 2    │
│  Trades Today: 15  Win Rate: 66.7%                 │
├─────────────────────────────────────────────────────┤
│  TOP 20 Candidates                                  │
│  ┌───┬────────┬───────┬──────────┬───────┐         │
│  │ # │ Ticker │ Score │ Δ Money  │ Δ Vol │         │
│  ├───┼────────┼───────┼──────────┼───────┤         │
│  │ 1 │ DOGE   │ 0.92  │ +125M    │ +50M  │         │
│  │ 2 │ XRP    │ 0.89  │ +98M     │ +32M  │         │
│  │...│        │       │          │       │         │
│  └───┴────────┴───────┴──────────┴───────┘         │
├─────────────────────────────────────────────────────┤
│  Holdings                                           │
│  ┌────────┬────────┬──────┬──────────┬──────────┐  │
│  │ Ticker │ Amount │ Avg  │ Current  │ Strategy │  │
│  ├────────┼────────┼──────┼──────────┼──────────┤  │
│  │ XRP    │ 150    │ 800  │ +3.2%    │ UltraScalp│ │
│  │ NEAR   │ 50     │ 1500 │ -1.5%    │ DeepHunter│ │
│  └────────┴────────┴──────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────┤
│  Recent Trades (Last 10)                            │
│  ┌──────────┬────────┬────────┬──────┬────────────┐│
│  │ Time     │ Ticker │ Action │ P/L  │ Exit Reason││
│  ├──────────┼────────┼────────┼──────┼────────────┤│
│  │ 12:34:56 │ DOGE   │ SELL   │+3.5% │ PARTIAL_5  ││
│  │ 12:30:12 │ XRP    │ BUY    │  -   │ -          ││
│  └──────────┴────────┴────────┴──────┴────────────┘│
├─────────────────────────────────────────────────────┤
│  [Chat collapsed - click to expand]                │
└─────────────────────────────────────────────────────┘
```

---

## 📂 File Structure (New)

```
/home/user/webapp/
├── v9/                              # New v9 system
│   ├── signal_engine/               # Signal Engine (runs on Local PC)
│   │   ├── snapshot_scorer.py
│   │   ├── btc_regime_detector.py
│   │   ├── ultra_scalp_monitor.py
│   │   ├── deep_hunter_monitor.py
│   │   ├── websocket_emitter.py
│   │   └── config.json
│   │
│   ├── execution_engine/            # Execution Engine (Novita Server)
│   │   ├── websocket_receiver.py
│   │   ├── signal_validator.py
│   │   ├── trade_executor.py
│   │   ├── portfolio_manager.py
│   │   ├── recovery_engine.py
│   │   ├── btc_stacker.py
│   │   ├── safety_gates.py
│   │   └── config.json
│   │
│   ├── shared/                      # Shared utilities
│   │   ├── strategy_registry.json
│   │   ├── signal_schema.py
│   │   ├── logging_utils.py
│   │   └── constants.py
│   │
│   ├── dashboard/                   # Compact Dashboard
│   │   ├── app.py
│   │   ├── templates/
│   │   │   └── dashboard.html
│   │   └── static/
│   │       ├── css/
│   │       └── js/
│   │
│   └── tests/                       # Testing & Validation
│       ├── test_signal_engine.py
│       ├── test_execution_engine.py
│       ├── test_websocket.py
│       └── integration_test.py
│
├── logs/                            # Centralized logging
│   ├── signal_engine/
│   ├── execution_engine/
│   └── trades/
│
└── docs/                            # Documentation
    ├── ARCHITECTURE_V9.md           # This file
    ├── MIGRATION_V8_TO_V9.md
    ├── STRATEGY_GUIDE.md
    └── TESTING_GUIDE.md
```

---

## 🔄 Migration from v8 to v9

### Phase 1: Parallel Run (1 week)
- Keep v8 running
- Run v9 in paper trading only
- Compare signals side-by-side
- Validate WebSocket stability

### Phase 2: Signal Engine Cutover
- Disable v8 signal generation
- Enable v9 signal engine
- Keep v8 execution for safety

### Phase 3: Full v9 Activation
- Switch execution engine to v9
- Enable double lock gates
- Start with 100k exposure limit
- Monitor for 48 hours

### Phase 4: Scale Up
- Increase exposure limit gradually
- Enable all strategies
- Full production mode

---

## 📊 Success Metrics (v9 Launch)

### Technical Stability:
- ✅ 99.9% WebSocket uptime
- ✅ <500ms signal latency
- ✅ Zero API rate limit hits
- ✅ Clean separation (no cross-engine calls)

### Trading Performance:
- ✅ Win rate ≥ 60% (Ultra Scalp)
- ✅ Average R:R ≥ 1.8
- ✅ Max drawdown < 15%
- ✅ Positive EV across all strategies

### Safety:
- ✅ No unauthorized live orders
- ✅ Double lock gates functional
- ✅ Daily -2% auto-halt tested
- ✅ Emergency stop <1s response

---

## 🚀 Commit Strategy (10 Groups)

1. `feat(v9): architecture split + docs`
2. `feat(v9): websocket layer`
3. `feat(v9): candidate selector (TOP 20)`
4. `feat(v9): regime filter (BTC detector)`
5. `feat(v9): ultra scalp strategy`
6. `feat(v9): deep hunter strategy`
7. `feat(v9): recovery engine`
8. `feat(v9): BTC stacking`
9. `feat(v9): strategy registry`
10. `feat(v9): compact dashboard`
11. `feat(v9): safety gates (double lock)`
12. `test(v9): validation + logs`

---

**Status**: 🔴 DESIGN COMPLETE → Ready for Implementation  
**Next**: Start with `feat(v9): architecture split + docs` commit
