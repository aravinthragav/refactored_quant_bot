import os
import datetime as dt

from forecast_engine import (
    get_forecast_payload
)

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

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

   # "BTC": "BTC-USD",

    "GOLD": "GC=F"
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

# =========================================================
# FORECAST HISTORY
# =========================================================

if (
    "forecast_history"
    not in st.session_state
):

    st.session_state.forecast_history = []

# =========================================================
# MULTI TF SUPPORT / RESISTANCE
# =========================================================
@st.cache_data(ttl=300)
def get_sr_levels(
    ticker,
    current_price
):

    levels = []

    timeframes = [

        ("1H", "60m", "30d"),

        ("4H", "4h", "90d"),

        ("D", "1d", "180d"),

        ("W", "1wk", "2y"),

        ("M", "1mo", "5y")
    ]

    for label, interval, period in timeframes:

        try:

            htf = yf.download(

                ticker,

                interval=interval,

                period=period,

                progress=False,

                auto_adjust=False
            )

            if htf.empty:

                continue

            # =====================================
            # FIX MULTIINDEX
            # =====================================

            if isinstance(
                htf.columns,
                pd.MultiIndex
            ):

                htf.columns = [
                    c[0]
                    for c in htf.columns
                ]

            # =====================================
            # RECENT SWING LEVELS
            # =====================================

            recent_high = (
                htf['High']
                .tail(20)
                .max()
            )

            recent_low = (
                htf['Low']
                .tail(20)
                .min()
            )

            levels.append({

                "tf": label,

                "type": "R",

                "price": float(recent_high)
            })

            levels.append({

                "tf": label,

                "type": "S",

                "price": float(recent_low)
            })

        except Exception as e:

            print(
                f"{label} SR failed:",
                e
            )

    # =========================================
    # FILTER NEARBY ONLY
    # =========================================

    filtered = []

    for lvl in levels:

        distance_pct = abs(

            lvl["price"]
            - current_price

        ) / current_price * 100

        # only nearby levels
        if distance_pct <= 2.5:

            filtered.append(lvl)

    if not filtered:

        return []

    return filtered

# =========================================================
# PAYLOAD
# =========================================================

config = {

    "ticker": ticker,

    "interval": "5m",

    "lookback": lookback,

    "pred_len": pred_len
}

try:

    payload = get_forecast_payload(
        config
    )

except Exception as e:

    st.error(
        f"Forecast failed: {e}"
    )

    st.stop()

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
# SR LEVELS
# =========================================================

sr_levels = get_sr_levels(
    ticker,
    current_price
)

# =========================================================
# FORECAST KEY
# =========================================================

forecast_key = (
    f"{asset_name}_"
    f"{dt.datetime.now().strftime('%Y%m%d%H%M')}"
)

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

# =========================================================
# CANDLES
# =========================================================

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

# =========================================================
# FORECAST
# =========================================================

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

# =========================================================
# EMA20
# =========================================================

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

# =========================================================
# EMA89
# =========================================================

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

# =========================================================
# HISTORICAL FORECASTS
# =========================================================

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
# SR LEVELS
# =========================================================

for lvl in sr_levels:

    color = (
        "#ff4d4d"
        if lvl["type"] == "R"
        else "#00cc96"
    )

    fig.add_hline(

        y=lvl["price"],

        line_dash="dot",

        line_color=color,

        opacity=0.5
    )

    fig.add_annotation(

        x=x_timestamp.iloc[-1],

        y=lvl["price"],

        text=(
            f"{lvl['tf']} "
            f"{lvl['type']} "
            f"{lvl['price']:.2f}"
        ),

        showarrow=False,

        xshift=80,
        yshift=12,
        font=dict(
            size=10,
            color=color
        ),
        bgcolor="rgba(0,0,0,0.4)"
    )

# =========================================================
# DYNAMIC RANGE
# =========================================================

visible_prices = [

    current_price,

    forecast_price
]

for lvl in sr_levels:

    visible_prices.append(
        lvl["price"]
    )
    
if not visible_prices:

    visible_prices = [
        current_price
    ]
y_min = min(visible_prices)

y_max = max(visible_prices)

padding = (
    y_max - y_min
) * 0.15

# =========================================================
# LAYOUT
# =========================================================

fig.update_layout(

    title=f"{asset_name} AI Forecast",

    xaxis_title="Time",

    yaxis_title="Price",

    xaxis_rangeslider_visible=False,

    template="plotly_dark",

    height=800,

    yaxis=dict(

        side="right",

        fixedrange=False,

        autorange=False,

        range=[

            y_min - padding,

            y_max + padding
        ]
    )
)

# =========================================================
# PLOT
# =========================================================

st.plotly_chart(
    fig,
    width="stretch"
)

# =========================================================
# FORECAST TABLE
# =========================================================

st.subheader(
    "Forecast Data"
)

st.dataframe(
    pred_df,
    width="stretch"
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

# =========================================================
# FOOTER
# =========================================================

st.caption(
    "Auto refresh every 5 minutes"
)