

import os
import datetime as dt


import pandas as pd
import yfinance as yf
import ta

from model import (
    Kronos,
    KronosTokenizer,
    KronosPredictor
)

from signal_engine import process_signal

# =========================================================
# MODEL PATHS
# MODEL PATHS
# =========================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

TOKENIZER_PATH = MODELS_DIR / "gold" / "tokenizer_base" / "best_model"
MODEL_PATH = MODELS_DIR / "gold" / "basemodel_base" / "best_model"


# =========================================================
# LOAD MODEL
# =========================================================

predictor = None

def get_predictor():
    global predictor

    if predictor is None:
        print("Loading tokenizer...")

        tokenizer = KronosTokenizer.from_pretrained(
            str(TOKENIZER_PATH),
            local_files_only=True
        )
        
        print("Loading model...")
        
        model = Kronos.from_pretrained(
            str(MODEL_PATH),
            local_files_only=True
        )
        
        predictor = KronosPredictor(
            model,
            tokenizer,
            device="cpu",
            max_context=512
        )

    return predictor
# =========================================================
# FETCH MARKET DATA
# =========================================================

def fetch_market_data(
    ticker,
    interval="5m",
    period="30d"
):

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False
    )

    if df.empty:

        return None

    # =====================================================
    # FIX MULTIINDEX
    # =====================================================

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = [
            col[0]
            for col in df.columns
        ]

    # =====================================================
    # RESET INDEX
    # =====================================================

    df = df.reset_index()

    # =====================================================
    # FIND TIMESTAMP COLUMN
    # =====================================================

    possible_time_cols = [

        'Datetime',
        'Date',
        'datetime',
        'date',
        'index'
    ]

    time_col = None

    for col in possible_time_cols:

        if col in df.columns:

            time_col = col

            break

    if time_col is None:

        raise Exception(
            f"Timestamp column not found. "
            f"Columns: {df.columns.tolist()}"
        )

    # =====================================================
    # RENAME
    # =====================================================

    df = df.rename(
        columns={
            time_col: 'timestamps'
        }
    )

    # =====================================================
    # LOWERCASE
    # =====================================================

    df.columns = [
        str(c).lower()
        for c in df.columns
    ]

    # =====================================================
    # DATETIME
    # =====================================================

    df['timestamps'] = pd.to_datetime(
        df['timestamps'],
        errors='coerce'
    )

    df = df.dropna(
        subset=['timestamps']
    )

    # =====================================================
    # NUMERIC
    # =====================================================

    numeric_cols = [
        'open',
        'high',
        'low',
        'close',
        'volume'
    ]

    for col in numeric_cols:

        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        )

    # =====================================================
    # EXTRA
    # =====================================================
    
    # Filter out extreme wicks (bad ticks from yfinance) that distort the chart
    for col in ['high', 'low', 'open', 'close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Calculate candle body size
    body_max = df[['open', 'close']].max(axis=1)
    body_min = df[['open', 'close']].min(axis=1)
    body_size = body_max - body_min
    
    # Cap highs and lows to a max of 3x the average body size, or 0.15% of price, to remove bad spikes
    max_wick = df['close'] * 0.0015
    df['high'] = df[['high', body_max + max_wick]].min(axis=1)
    df['low'] = df[['low', body_min - max_wick]].max(axis=1)

    df['amount'] = 0

    return df

# =========================================================
# INDICATORS
# =========================================================

def add_indicators(df):

    df['ema20'] = ta.trend.EMAIndicator(
        df['close'],
        window=20
    ).ema_indicator()

    df['median_price'] = (
        df['high']
        + df['low']
    ) / 2

    df['ema89_median'] = ta.trend.EMAIndicator(
        df['median_price'],
        window=89
    ).ema_indicator()

    df['rsi'] = ta.momentum.RSIIndicator(
        df['close']
    ).rsi()

    df['returns'] = (
        df['close']
        .pct_change()
    )

    df['volatility'] = (
        df['returns']
        .rolling(20)
        .std()
    )

    df['atr'] = ta.volatility.AverageTrueRange(
        df['high'],
        df['low'],
        df['close'],
        window=14
    ).average_true_range()

    return df.dropna()

# =========================================================
# PREPARE PREDICTION DATA
# =========================================================

def prepare_prediction_data(
    df,
    lookback,
    pred_len,
    interval="5m"
):

    x_df = df[
        [
            'open',
            'high',
            'low',
            'close',
            'volume',
            'amount'
        ]
    ].tail(lookback).copy()

    local_tz = (
        dt.datetime.now(
            dt.timezone.utc
        )
        .astimezone()
        .tzinfo
    )

    x_timestamp = pd.Series(
        pd.to_datetime(
            df['timestamps']
            .tail(lookback)
        )
    )

    if x_timestamp.dt.tz is None:

        x_timestamp = (
            x_timestamp
            .dt
            .tz_localize('UTC')
            .dt
            .tz_convert(local_tz)
        )

    else:

        x_timestamp = (
            x_timestamp
            .dt
            .tz_convert(local_tz)
        )

    last_ts = x_timestamp.iloc[-1]

    freq_map = {
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "1d": "1D",
        "D": "1D"
    }
    freq = freq_map.get(interval, "5min")

    y_timestamp = pd.Series(
        pd.date_range(
            start=last_ts,
            periods=pred_len + 1,
            freq=freq
        )[1:]
    )

    return (
        x_df,
        x_timestamp,
        y_timestamp
    )

# =========================================================
# GENERATE FORECAST
# =========================================================

def generate_forecast(
    x_df,
    x_timestamp,
    y_timestamp,
    pred_len
):
    predictor = get_predictor()
    pred_df = predictor.predict(
        df=x_df,
        x_timestamp=x_timestamp,
        y_timestamp=y_timestamp,
        pred_len=pred_len,
        T=0.8,
        top_p=0.9,
        sample_count=5
    )

    return pred_df

# =========================================================
# CENTRALIZED FORECAST PAYLOAD
# =========================================================

def get_forecast_payload(config):
    ticker = config["ticker"]

    interval = config["interval"]

    lookback = config["lookback"]

    pred_len = config["pred_len"]


    # =====================================================
    # FETCH DATA
    # =====================================================

    df = fetch_market_data(
        ticker=ticker,
        interval=interval
    )

    if df is None:

        return None

    # =====================================================
    # INDICATORS
    # =====================================================

    df = add_indicators(df)

    # =====================================================
    # PREP
    # =====================================================

    (
        x_df,
        x_timestamp,
        y_timestamp
    ) = prepare_prediction_data(

        df=df,

        lookback=lookback,

        pred_len=pred_len,

        interval=interval
    )

    # =====================================================
    # FORECAST
    # =====================================================

    pred_df = generate_forecast(

        x_df=x_df,

        x_timestamp=x_timestamp,

        y_timestamp=y_timestamp,

        pred_len=pred_len
    )

    # =====================================================
    # METRICS
    # =====================================================

    current_price = float(
        df['close'].iloc[-1]
    )

    forecast_price = float(
        pred_df['close'].iloc[-1]
    )

    move_pct = (
        (
            forecast_price
            - current_price
        )
        / current_price
    ) * 100

    direction = (
        "🟢 Bullish"
        if move_pct > 0
        else "🔴 Bearish"
    )

    confidence = min(
        95,
        max(
            50,
            100 - (
                df['volatility']
                .iloc[-1]
                * 1000
            )
        )
    )

    return {

        "df": df,

        "x_df": x_df,

        "pred_df": pred_df,

        "x_timestamp": x_timestamp,

        "y_timestamp": y_timestamp,

        "current_price": current_price,

        "forecast_price": forecast_price,

        "move_pct": move_pct,

        "direction": direction,

        "confidence": confidence
    }

# =========================================================
# SUPPORT & RESISTANCE LEVELS
# =========================================================

def get_sr_levels(ticker, current_price):
    import math
    levels = []
    timeframes = [
        ("15m", "15m", "7d"),
        ("30m", "30m", "14d"),
        ("1H", "60m", "30d"),
        ("4H", "4h", "90d"),
        ("D", "1d", "180d"),
        ("W", "1wk", "2y"),
        ("M", "1mo", "5y")
    ]
    for label, interval, period in timeframes:
        try:
            htf = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=False)
            if htf.empty: continue
            if isinstance(htf.columns, pd.MultiIndex):
                htf.columns = [c[0] for c in htf.columns]
            
            recent_high = htf['High'].tail(20).max()
            recent_low = htf['Low'].tail(20).min()
            
            levels.append({"tf": label, "type": "R", "price": float(recent_high)})
            levels.append({"tf": label, "type": "S", "price": float(recent_low)})
        except Exception:
            pass

    filtered = []
    for lvl in levels:
        if math.isnan(lvl["price"]): continue
        distance_pct = abs(lvl["price"] - current_price) / current_price * 100
        if distance_pct <= 6.0:
            filtered.append(lvl)

    # Group and merge S/R levels that are within 0.15% of each other
    levels_R = sorted([l for l in filtered if l["type"] == "R"], key=lambda x: x["price"])
    levels_S = sorted([l for l in filtered if l["type"] == "S"], key=lambda x: x["price"])

    def merge_levels(lvl_list):
        if not lvl_list:
            return []
        merged = []
        current = lvl_list[0]
        for next_lvl in lvl_list[1:]:
            if abs(next_lvl["price"] - current["price"]) / current["price"] * 100 <= 0.15:
                # Merge: combine timeframes
                tfs = current["tf"].split("/") + next_lvl["tf"].split("/")
                order_map = {"15m": 0, "30m": 1, "1H": 2, "4H": 3, "D": 4, "W": 5, "M": 6}
                unique_tfs = sorted(list(set(tfs)), key=lambda x: order_map.get(x, 99))
                current["tf"] = "/".join(unique_tfs)
                # Set price to average
                current["price"] = (current["price"] + next_lvl["price"]) / 2
            else:
                merged.append(current)
                current = next_lvl
        merged.append(current)
        return merged

    merged_R = merge_levels(levels_R)
    merged_S = merge_levels(levels_S)
    return merged_R + merged_S

# =========================================================
# SAVE FORECAST CACHE
# =========================================================

def save_forecast_cache(asset_name, payload, config):
    try:
        import math
        import json
        
        ticker = config["ticker"]
        lookback = config["lookback"]
        pred_len = config["pred_len"]
        
        x_timestamp = payload["x_timestamp"]
        x_df = payload["x_df"]
        pred_df = payload["pred_df"]
        y_timestamp = payload["y_timestamp"]
        df = payload["df"]
        
        hist_data = []
        for i in range(len(x_df)):
            hist_data.append({
                "time": int(x_timestamp.iloc[i].timestamp()),
                "open": float(x_df['open'].iloc[i]),
                "high": float(x_df['high'].iloc[i]),
                "low": float(x_df['low'].iloc[i]),
                "close": float(x_df['close'].iloc[i])
            })
            
        forecast_data = []
        forecast_data.append({
            "time": int(x_timestamp.iloc[-1].timestamp()),
            "value": float(x_df['close'].iloc[-1])
        })
        for i in range(len(pred_df)):
            forecast_data.append({
                "time": int(y_timestamp.iloc[i].timestamp()),
                "value": float(pred_df['close'].iloc[i])
            })
            
        ema20_data = []
        ema20_series = df['ema20'].tail(lookback)
        for i in range(len(ema20_series)):
            val = ema20_series.iloc[i]
            if not math.isnan(val):
                ema20_data.append({
                    "time": int(x_timestamp.iloc[i].timestamp()),
                    "value": float(val)
                })
                
        ema89_data = []
        ema89_series = df['ema89_median'].tail(lookback)
        for i in range(len(ema89_series)):
            val = ema89_series.iloc[i]
            if not math.isnan(val):
                ema89_data.append({
                    "time": int(x_timestamp.iloc[i].timestamp()),
                    "value": float(val)
                })

        sr_levels = get_sr_levels(ticker, payload["current_price"])

        mae = None
        try:
            actual = df['close'].tail(pred_len).values
            predicted = pred_df['close'].values[:len(actual)]
            mae = float(sum(abs(actual - predicted)) / len(actual))
        except:
            pass

        is_weekend = dt.datetime.now().weekday() in [5, 6]

        cache_data = {
            "success": True,
            "asset_name": asset_name,
            "current_price": float(payload["current_price"]),
            "forecast_price": float(payload["forecast_price"]),
            "move_pct": float(payload["move_pct"]),
            "direction": payload["direction"],
            "hist_data": hist_data,
            "forecast_data": forecast_data,
            "ema20_data": ema20_data,
            "ema89_data": ema89_data,
            "sr_levels": sr_levels,
            "mae": mae,
            "market_closed": is_weekend if asset_name == "GOLD" else False
        }

        os.makedirs(str(BASE_DIR / "cache"), exist_ok=True)
        interval = config.get("interval", "5m")
        cache_path = BASE_DIR / "cache" / f"{asset_name.lower()}_{interval}_forecast.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)
        print(f"Cached forecast for {asset_name} ({interval}) to {cache_path}")
    except Exception as e:
        print(f"Failed to cache forecast for {asset_name}: {e}")

# =========================================================
# PROCESS ASSET
# =========================================================

def process_asset(
    asset_name,
    config
):

    payload = get_forecast_payload(config)

    if payload is None:

        return

    # Write to local cache so the FastAPI server can serve it instantly
    save_forecast_cache(asset_name, payload, config)

    process_signal(

        asset_name=asset_name,

        config=config,

        df=payload["df"],

        pred_df=payload["pred_df"],

        y_timestamp=payload["y_timestamp"]
    )
