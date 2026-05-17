import os
import datetime as dt

import pandas as pd
import yfinance as yf
import ta
import mplfinance as mpf
import matplotlib.pyplot as plt

from model import (
    Kronos,
    KronosTokenizer,
    KronosPredictor
)

from signal_engine import process_signal

BASE_DIR = r"C:\Users\ragav\Downloads\refactored_quant_bot\Linto\models"

TOKENIZER_PATH = os.path.join(
    BASE_DIR,
    "tokenizer_base",
    "best_model"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "basemodel_base",
    "best_model"
)

print("Loading tokenizer...")
tokenizer = KronosTokenizer.from_pretrained(
    TOKENIZER_PATH
)

print("Loading model...")
model = Kronos.from_pretrained(
    MODEL_PATH
)

predictor = KronosPredictor(
    model,
    tokenizer,
    device="cpu",
    max_context=512
)

def process_asset(
    asset_name,
    config
):

    ticker = config["ticker"]

    df = yf.download(
        ticker,
        interval=config["interval"],
        period="30d",
        progress=False
    )

    if df.empty:

        return

    if isinstance(df.columns, pd.MultiIndex):

        df.columns = (
            df.columns
            .get_level_values(0)
        )

    df["timestamps"] = df.index

    df = df.reset_index(drop=True)

    df.columns = [
        str(c).lower()
        for c in df.columns
    ]

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

    df['timestamps'] = pd.to_datetime(
        df['timestamps'],
        errors='coerce'
    )

    df['amount'] = 0

    df['ema20'] = ta.trend.EMAIndicator(
        df['close'],
        window=20
    ).ema_indicator()

    df['median_price'] = (
        df['high'] + df['low']
    ) / 2

    df['ema89_median'] = ta.trend.EMAIndicator(
        df['median_price'],
        window=89
    ).ema_indicator()

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

    df = df.dropna()

    lookback = config["lookback"]

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

    pred_len = config["pred_len"]

    last_ts = x_timestamp.iloc[-1]

    y_timestamp = pd.Series(
        pd.date_range(
            start=last_ts,
            periods=pred_len + 1,
            freq="5min"
        )[1:]
    )

    pred_df = predictor.predict(
        df=x_df,
        x_timestamp=x_timestamp,
        y_timestamp=y_timestamp,
        pred_len=pred_len,
        T=0.8,
        top_p=0.9,
        sample_count=5
    )

    process_signal(
        asset_name=asset_name,
        config=config,
        df=df,
        pred_df=pred_df,
        y_timestamp=y_timestamp
    )