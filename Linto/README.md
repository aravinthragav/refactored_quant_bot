````markdown id="b7t3sa"
# AI Quant Trading Signal Engine

Multi-asset AI forecasting and signal execution engine powered by:
- Kronos finetuned forecasting model
- Technical analysis
- ATR-based risk management
- SQLite trade lifecycle tracking
- Telegram delivery
- Macro-event awareness
- Trade validation analytics

---

# Features

## AI Forecasting
- Kronos finetuned transformer model
- Multi-horizon forecasting
- Probabilistic prediction generation

## Multi Asset Support
Supports:
- BTC
- ETH
- GOLD
- NASDAQ
- Custom Yahoo Finance tickers

Configured via:

```python
asset_configs.py
````

---

# Trade Engine

## ATR-Based TP/SL

Dynamic volatility-aware:

* Take profit
* Stop loss

## Risk Reward Filtering

Rejects weak setups automatically.

Example:

```python
if rr < 1.3:
    skip
```

---

# Telegram Signal Delivery

Sends:

* AI forecast chart
* Trade overlay chart
* TP/SL zones
* RR ratio
* Confidence score
* Macro risk state

---

# Trade Validation Engine

Tracks:

* TP HIT
* SL HIT
* EXPIRED trades

Uses:

* candle HIGH/LOW validation
* not close-price validation

This improves realism significantly.

---

# SQLite Persistence

Persistent lifecycle tracking:

* signals
* TP/SL
* status
* outcomes
* analytics

Stored in:

```text
db/signals.db
```

---

# Project Structure

```text
project/

├── main.py
├── asset_configs.py
├── forecast_engine.py
├── signal_engine.py
├── trade_validator.py
├── trade_chart.py
├── trade_chart_overlay.py
├── macro_calendar.py
├── telegram_sender.py

├── db/
│   ├── signal_storage.py
│   └── analytics.py

├── strategies/
│   ├── trend_following.py
│   ├── mean_reversion.py
│   └── breakout.py

├── charts/
├── finetune/
└── requirements.txt
```

---

# Installation

## 1. Clone Project

```bash
git clone <repo>
cd project
```

---

## 2. Create Environment

```bash
python -m venv venv
```

Activate:

### Linux/Mac

```bash
source venv/bin/activate
```

### Windows

```bash
venv\\Scripts\\activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

# Finetuned Model Setup

Place finetuned Kronos model inside:

```text
finetune/
├── tokenizer_base/
│   └── best_model/
├── basemodel_base/
│   └── best_model/
```

---

# Telegram Setup

Open:

```python
telegram_sender.py
```

Replace:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
```

with your values.

---

# Running the Bot

```bash
python main.py
```

The engine will:

1. Validate existing trades
2. Fetch latest market data
3. Generate AI forecasts
4. Apply RR filtering
5. Generate charts
6. Send Telegram signals
7. Store trades in SQLite

Runs every:

* 5 minutes

---

# Supported Strategies

Currently included:

* Trend Following
* Mean Reversion
* Breakout

Future strategies can be added inside:

```text
strategies/
```

---

# Signal Lifecycle

```text
OPEN
  ↓
TP_HIT
SL_HIT
EXPIRED
```

---

# Validation Logic

## Long Trades

```python
if high >= tp:
    TP_HIT

elif low <= sl:
    SL_HIT
```

## Short Trades

```python
if low <= tp:
    TP_HIT

elif high >= sl:
    SL_HIT
```

---

# Risk Model

## Long

```python
tp = forecast_price
sl = current_price - atr * multiplier
```

## Short

```python
tp = forecast_price
sl = current_price + atr * multiplier
```

---

# Future Roadmap

## Planned Features

### Analytics Dashboard

* Win rate
* Expectancy
* Session analysis
* Macro regime analysis

### Advanced Validation

* MAE/MFE tracking
* Intrabar replay
* Signal efficiency

### Parallel Execution

* asyncio
* ThreadPoolExecutor

### Dynamic Regime Detection

* Trending
* Ranging
* Panic volatility
* Macro suppression

### Portfolio-Level Risk

* exposure management
* correlation filtering

---

# Notes

## SQLite Schema Changes

If schema changes occur:

Delete:

```text
db/signals.db
```

Then rerun bot.

SQLite does not auto-migrate schemas.

---

# Disclaimer

This project is experimental research software.
Not financial advice.
Use at your own risk.

```
```
