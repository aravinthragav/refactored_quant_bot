import os
import time
import datetime as dt
from forecast_engine import (
    get_forecast_payload
)
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta

from streamlit_autorefresh import (
    st_autorefresh
)


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="AI Quant Dashboard",
    layout="wide"
)

st.title(
    "🟡 AI Quant Forecast Dashboard"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=300000,
    key="refresh"
)

# =========================================================
# ASSETS
# =========================================================

ASSETS = {

    "BTC": "BTC-USD",

    "GOLD": "XAUUSD=X"
}

asset_name = st.sidebar.selectbox(
    "Asset",
    list(ASSETS.keys())
)

ticker = ASSETS[
    asset_name
]

# =========================================================
# SETTINGS
# =========================================================

lookback = st.sidebar.slider(
    "Lookback",
    100,
    512,
    256
)

pred_len = st.sidebar.slider(
    "Prediction Length",
    10,
    120,
    12
)

# =========================================================
# CACHE
# =========================================================

CACHE_DIR = "cache"

os.makedirs(
    CACHE_DIR,
    exist_ok=True
)

cache_file = os.path.join(
    CACHE_DIR,
    f"{ticker}_cache.csv"
)

def load_cached_data():

    if os.path.exists(
        cache_file
    ):

        try:

            return pd.read_csv(
                cache_file,
                parse_dates=True,
                index_col=0
            )

        except:

            return None

    return None

def save_cached_data(df):

    try:

        df.to_csv(cache_file)

    except:

        pass

# =========================================================
# FORECAST HISTORY
# =========================================================

if (
    "forecast_history"
    not in st.session_state
):

    st.session_state.forecast_history = []

payload = get_forecast_payload(

    ticker=ticker,

    interval="5m",

    lookback=lookback,

    pred_len=pred_len
)

df = payload["df"]

x_df = payload["x_df"]

pred_df = payload["pred_df"]

x_timestamp = payload["x_timestamp"]

y_timestamp = payload["y_timestamp"]

current_price = payload["current_price"]

forecast_price = payload["forecast_price"]

move_pct = payload["move_pct"]

direction = payload["direction"]

confidence = payload["confidence"]

# =========================================================
# TOP METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current",
    f"{current_price:.2f}"
)

col2.metric(
    "Forecast",
    f"{forecast_price:.2f}"
)

col3.metric(
    "Move %",
    f"{move_pct:.2f}%"
)

col4.metric(
    "Confidence",
    f"{confidence:.1f}%"
)

# =========================================================
# TREND
# =========================================================

trend = (
    x_df['close']
    .rolling(50)
    .mean()
)

trend_direction = (
    "Uptrend"
    if x_df['close'].iloc[-1]
    > trend.iloc[-1]
    else "Downtrend"
)

st.subheader(
    f"Trend: {trend_direction}"
)

# =========================================================
# CHART
# =========================================================

fig = go.Figure()

# Candles
fig.add_trace(
    go.Candlestick(

        x=x_timestamp,

        open=x_df['open'],

        high=x_df['high'],

        low=x_df['low'],

        close=x_df['close'],

        name="Historical"
    )
)

# Forecast
fig.add_trace(
    go.Scatter(

        x=y_timestamp,

        y=pred_df['close'],

        mode='lines',

        name='Forecast',

        line=dict(
            color='#ff9900',
            width=3
        )
    )
)

# EMA20
fig.add_trace(
    go.Scatter(

        x=x_timestamp,

        y=df['ema20']
        .tail(lookback),

        mode='lines',

        name='EMA20',

        line=dict(
            color='cyan'
        )
    )
)

# EMA89
fig.add_trace(
    go.Scatter(

        x=x_timestamp,

        y=df['ema89_median']
        .tail(lookback),

        mode='lines',

        name='EMA89 Median',

        line=dict(
            color='purple'
        )
    )
)

# Historical forecasts
for entry in (
    st.session_state
    .forecast_history[-5:]
):

    if entry['key'] == forecast_key:

        continue

    fig.add_trace(
        go.Scatter(

            x=entry['timestamps'],

            y=entry['values'],

            mode='lines',

            line=dict(
                dash='dash',
                width=1,
                color='gray'
            ),

            opacity=0.4,

            hoverinfo='none',

            name=entry['label']
        )
    )

# =========================================================
# LAYOUT
# =========================================================

fig.update_layout(

    title=f"{asset_name} AI Forecast",

    xaxis_title="Time",

    yaxis_title="Price",

    xaxis_rangeslider_visible=False,

    template="plotly_dark",

    height=800
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# FORECAST TABLE
# =========================================================

st.subheader(
    "Forecast Data"
)

st.dataframe(
    pred_df,
    use_container_width=True
)

# =========================================================
# MAE
# =========================================================

try:

    actual = (
        df['close']
        .tail(pred_len)
        .values
    )

    predicted = (
        pred_df['close']
        .values[:len(actual)]
    )

    from sklearn.metrics import (
        mean_absolute_error
    )

    mae = mean_absolute_error(
        actual,
        predicted
    )

    st.metric(
        "MAE",
        round(mae, 4)
    )

except:

    st.info(
        "MAE unavailable"
    )

st.caption(
    "Auto refresh every 5 minutes"
)