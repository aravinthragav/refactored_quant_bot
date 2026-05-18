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
# MODEL CACHE
# =========================================================

MODEL_CACHE = {}

# =========================================================
# GET PREDICTOR
# =========================================================

def get_predictor(config):

    model_key = (
        config.get("model_name")
        or config.get("model_path")
    )

    if model_key in MODEL_CACHE:

        return MODEL_CACHE[model_key]

    print(
        f"Loading model: {model_key}"
    )

    # =====================================================
    # LOCAL MODEL
    # =====================================================

    if config["model_source"] == "local":

        tokenizer = (
            KronosTokenizer
            .from_pretrained(
                config["tokenizer_path"]
            )
        )

        model = (
            Kronos
            .from_pretrained(
                config["model_path"]
            )
        )

    # =====================================================
    # HUGGINGFACE MODEL
    # =====================================================

    elif config["model_source"] == "huggingface":

        tokenizer = (
            KronosTokenizer
            .from_pretrained(
                config["model_name"]
            )
        )

        model = (
            Kronos
            .from_pretrained(
                config["model_name"]
            )
        )

    else:

        raise Exception(
            "Unknown model source"
        )

    predictor = KronosPredictor(

        model,

        tokenizer,

        device="cpu",

        max_context=512
    )

    MODEL_CACHE[model_key] = predictor

    return predictor

# =========================================================
# FETCH DATA
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

        auto_adjust=False,

        progress=False,

        threads=False
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
    # FIND TIMESTAMP
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

    df = df.rename(
        columns={
            time_col: 'timestamps'
        }
    )

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
# PREP DATA
# =========================================================

def prepare_prediction_data(
    df,
    lookback,
    pred_len
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

    y_timestamp = pd.Series(
        pd.date_range(
            start=last_ts,
            periods=pred_len + 1,
            freq="5min"
        )[1:]
    )

    return (
        x_df,
        x_timestamp,
        y_timestamp
    )

# =========================================================
# FORECAST
# =========================================================

def generate_forecast(
    predictor,
    x_df,
    x_timestamp,
    y_timestamp,
    pred_len
):

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
# FORECAST PAYLOAD
# =========================================================

def get_forecast_payload(config):

    ticker = config["ticker"]

    predictor = get_predictor(
        config
    )

    # =====================================================
    # FETCH
    # =====================================================

    df = fetch_market_data(

        ticker=ticker,

        interval=config["interval"]
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

        lookback=config["lookback"],

        pred_len=config["pred_len"]
    )

    # =====================================================
    # FORECAST
    # =====================================================

    pred_df = generate_forecast(

        predictor=predictor,

        x_df=x_df,

        x_timestamp=x_timestamp,

        y_timestamp=y_timestamp,

        pred_len=config["pred_len"]
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
# PROCESS ASSET
# =========================================================

def process_asset(
    asset_name,
    config
):

    payload = get_forecast_payload(
        config
    )

    if payload is None:

        print(
            f"{asset_name}: no data."
        )

        return

    process_signal(

        asset_name=asset_name,

        config=config,

        df=payload["df"],

        pred_df=payload["pred_df"],

        y_timestamp=payload["y_timestamp"]
    )