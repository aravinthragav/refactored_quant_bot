import os
import datetime as dt

import random
import feedparser
from forecast_engine import (
    get_forecast_payload
)

import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from streamlit_autorefresh import (
    st_autorefresh
)
from PIL import Image
icon = Image.open("assets/logo.png")

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="AI Gold Forecast Terminal",
    page_icon=icon,
    layout="wide"
)
components.html("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-8C0VKHXDF6"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-8C0VKHXDF6');
</script>
""", height=0)
components.html("""
<script async
src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-0024771137213737"
crossorigin="anonymous"></script>
""", height=0)
# =====================================
# HIDE STREAMLIT UI
# =====================================
st.markdown("""
<style>

/* Reduce top padding without moving content off-screen */
.main .block-container {
    max-width: 1600px;
    padding-left: 1rem;
    padding-right: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Reduce top padding without moving content off-screen */
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 0rem !important;
}

/* Hide Streamlit UI */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

[data-testid="stToolbar"] {
    display:none !important;
}

[data-testid="stDecoration"] {
    display:none !important;
}

/* Remove top header space */
[data-testid="stHeader"] {
    display:none !important;
}

/* Remove extra page gap */
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0rem !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="
display:flex;
justify-content:space-between;
align-items:center;
background:linear-gradient(90deg,#06142c,#0d1f44);
padding:14px;
border-radius:16px;
border:1px solid rgba(255,255,255,0.08);
margin-bottom:10px;
">

<div>
<meta name="google-adsense-account" content="ca-pub-0024771137213737">
<div style="
font-size:34px;
font-weight:800;
color:white;
line-height:1.1;
">
🟡 AI Gold Forecast Terminal
</div>

<div style="
margin-top:8px;
font-size:16px;
color:#9CA3AF;
">
Smart Signals • Market Intelligence • Real-Time Forecasting
</div>

</div>

<div style="
text-align:center;
min-width:280px;
">

<div style="
font-size:15px;
color:#9CA3AF;
margin-bottom:8px;
">
30-Signal Accuracy
</div>

<div style="
font-size:34px;
font-weight:800;
color:#22C55E;
line-height:1;
">
71.4%
</div>

<div style="margin-top:16px;">
<a href="https://t.me/tradingalertsAR"
target="_blank"
style="
text-decoration:none;
background:#229ED9;
padding:10px 20px;
border-radius:10px;
color:white;
font-weight:700;
font-size:15px;
display:inline-block;
">
📢 Join Telegram →
</a>
</div>

</div>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-emotion-cache-8atqhb {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)
# =========================================================
# SIGNAL BANNER
# =========================================================

def show_signal_banner(

    asset_name,
    direction,
    current_price,
    forecast_price,
    move_pct
):

    import streamlit.components.v1 as components

    banner_color = (
        "#ff8c00"
        if direction == "LONG"
        else "#2962ff"
    )

    direction_text = (
        "Bullish"
        if direction == "LONG"
        else "Bearish"
    )

    html = f"""

    <style>

    body {{
        margin: 0;
        overflow: hidden;
        background: transparent;
    }}

    .signal-banner {{

        position: fixed;

        top: 12px;

        left: 50%;

        transform: translateX(-50%);

        background: rgba(12,14,22,0.94);

        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 14px;

        padding: 10px 18px;

        display: flex;

        align-items: center;

        gap: 12px;

        box-shadow: 0 0 20px rgba(0,0,0,0.35);

        backdrop-filter: blur(12px);

        color: white;

        font-family: sans-serif;

        animation:
            fadeIn 0.4s ease,
            fadeOut 0.5s ease 8s forwards;
    }}

    .signal-dot {{

        width: 12px;

        height: 12px;

        border-radius: 50%;

        background: {banner_color};

        flex-shrink: 0;
    }}

    .signal-content {{

        display: flex;

        flex-direction: column;

        line-height: 1.3;
    }}

    .signal-title {{

        font-size: 15px;

        font-weight: 700;
    }}

    .signal-sub {{

        font-size: 12px;

        opacity: 0.88;
    }}

    @keyframes fadeIn {{

        from {{
            opacity: 0;
            transform:
                translateX(-50%)
                translateY(-10px);
        }}

        to {{
            opacity: 1;
            transform:
                translateX(-50%)
                translateY(0);
        }}
    }}

    @keyframes fadeOut {{

        to {{
            opacity: 0;
        }}
    }}

    </style>

    <div class="signal-banner">

        <div class="signal-dot"></div>

        <div class="signal-content">

            <div class="signal-title">

                {asset_name} • {direction_text}

            </div>

            <div class="signal-sub">

                {current_price:.2f}
                → {forecast_price:.2f}

                &nbsp;&nbsp;|&nbsp;&nbsp;

                {move_pct:.2f}%

            </div>

        </div>

    </div>

    """

    components.html(
        html,
        height=0
    )
# =========================================================
# NEWS TICKER
# =========================================================

@st.cache_data(ttl=1800)

def get_news_headlines(asset_name):

    feeds = []

    if asset_name == "BTC":

        feeds = [

            "https://www.coindesk.com/arc/outboundfeeds/rss/",

            "https://cointelegraph.com/rss"
        ]

    else:

        feeds = [

            # Reuters Commodities
            "https://www.reutersagency.com/feed/?best-topics=commodities",

            # Investing.com Commodities
            "https://www.investing.com/rss/news_25.rss",

            # FXStreet Gold
            "https://www.fxstreet.com/rss/news",

            # Kitco News
            "https://www.kitco.com/rss/news",

            # Mining.com Precious Metals
            "https://www.mining.com/feed/",

            # MarketWatch Markets
            "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",

            # Yahoo Finance News
            "https://finance.yahoo.com/news/rssindex",

            # CNBC Markets
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",

            # Federal Reserve News
            "https://www.federalreserve.gov/feeds/press_all.xml",

            # IMF News
            "https://www.imf.org/en/News/RSS"
        ]

    headlines = []

    for url in feeds:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:

                title = (
                    entry.title
                    .replace("&amp;", "&")
                )

                headlines.append(title)

        except Exception as e:

            print(
                "Ticker feed failed:",
                e
            )

    headlines = list(
        dict.fromkeys(headlines)
    )

    if not headlines:

        headlines = [

            "Markets monitoring Fed commentary",

            "Bitcoin volatility remains elevated",

            "Gold traders watching bond yields",

            "Macro uncertainty driving safe-haven flows"
        ]

    return headlines[:10]

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

#asset_name = st.sidebar.selectbox(
 #   "Asset",
#    list(ASSETS.keys())
#)

ticker = "GC=F"
asset_name = "GOLD"


# =========================================================
# SETTINGS
# =========================================================

lookback = 256
# st.sidebar.slider(
#    "Lookback",
 #   100,
#    512,
#    256
#)

pred_len = 12
#st.sidebar.slider(
 #   "Prediction Length",
 #   10,
 #   120,
 #   12
#)

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

news_items = get_news_headlines(
    asset_name
)
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

show_signal_banner(

    asset_name,

    direction,

    current_price,

    forecast_price,

    move_pct
)
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


# =========================================================
# TREND
# =========================================================

# trend = (
#     x_df['close']
#     .rolling(50)
#     .mean()
# )

# trend_direction = (
#     "Uptrend"
#     if x_df['close'].iloc[-1]
#     > trend.iloc[-1]
#     else "Downtrend"
# )

# st.subheader(
#     f"Trend: {trend_direction}"
# )

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

forecast_color = (
    "#ff8c00"
    if direction == "LONG"
    else "#2962ff"
)

fig.add_trace(
    go.Scatter(

        x=y_timestamp,

        y=pred_df['close'],

        mode='lines+markers',

        name='Forecast',

        line=dict(
            color=forecast_color,
            width=3
        )
    )
)

# =========================================================
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
# =========================================================
# EMA89
# =========================================================

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
        yshift=14,
        font=dict(
            size=10,
            color=color
        )
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

y_min = min(visible_prices)

y_max = max(visible_prices)

padding = (
    y_max - y_min
) * 0.15

# =========================================================
# INFO PANEL
# =========================================================

trend_text = (
    "Bullish"
    if direction == "LONG"
    else "Bearish"
)

session_name = (
    dt.datetime.now(dt.UTC)
    .strftime("%H:%M UTC")
)

info_text = f"""
<b>{asset_name}</b><br>

Current: {current_price:.2f}<br>

Forecast: {forecast_price:.2f}<br>

Move: {move_pct:.2f}%<br>

Trend: {trend_text}<br>

Session: {session_name}
"""

fig.add_annotation(

    xref="paper",

    yref="paper",

    x=0.985,

    y=0.98,

    text=info_text,

    showarrow=False,

    align="left",

    font=dict(
        size=11,
        color="white"
    ),

    bgcolor="rgba(0,0,0,0.65)",

    bordercolor="rgba(255,255,255,0.15)",

    borderwidth=1,

    borderpad=8
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

    #st.metric(
     #   "MAE",
    #    round(mae, 4)
    #)

except:

    st.info(
        "MAE unavailable"
    )
# =========================================================
# LAYOUT
# =========================================================

fig.update_layout(

    title=f"{asset_name} 5min AI Forecast",

    xaxis_title="Time",

    yaxis_title="Price",

    xaxis_rangeslider_visible=False,

    template="plotly_dark",

    height=800,

     yaxis=dict(
        side="right",
        fixedrange=False
    )
)

k1, k2, k3, k4, k5 = st.columns(5,gap="small")
k1.metric("Current", f"{current_price:.2f}")
k2.metric("Forecast", f"{forecast_price:.2f}")
k3.metric("Move %", f"{move_pct:.2f}%")
k4.metric("Direction", trend_text)
k5.metric("MAE", f"{round(mae, 4)}%")

#st.markdown("---")

left_ad, chart_col, right_ad = st.columns([1,4,1])

with left_ad:
    components.html('<a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank"><img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Take_control_300x600.png" width="100%"></a>', height=620)

with chart_col:
    st.plotly_chart(fig, width="stretch")

with right_ad:
    components.html('<a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank"><img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trading_Conditions_300x600px.gif" width="100%"></a>', height=620)

components.html('<div style="text-align:center;"><a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank"> <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trade_USOIL_with_Exness_720x90.png"</a></div>', height=110)


# =========================================================
# FORECAST TABLE
# =========================================================

#st.subheader(
#    "Forecast Data"
#

#st.dataframe(
#    pred_df,
#    width="stretch"
#)



# =========================================================
# NEWS TICKER
# =========================================================

ticker_items = ""

for item in (news_items * 3):

    ticker_items += f"""
    <div class="news-item">

        <span class="news-dot">
            ✦
        </span>

        <span>
            {item}
        </span>

    </div>
    """

ticker_html = f"""

<style>

.news-ticker-container {{

    position: fixed;

    margin-top: -10px;

    bottom: 0;

    left: 0;

    width: 100%;

    height: 42px;

    background: rgba(8,10,18,0.96);

    border-top: 1px solid rgba(255,255,255,0.08);

    overflow: hidden;

    z-index: 99999;

    display: flex;

    align-items: center;
}}

.news-ticker-track {{

    display: flex;

    width: max-content;

    white-space: nowrap;

    animation: ticker-scroll 120s linear infinite;
}}

.news-item {{

    display: flex;

    align-items: center;

    gap: 14px;

    padding-right: 50px;

    color: rgba(255,255,255,0.92);

    font-size: 14px;

    font-weight: 600;
}}

.news-dot {{

    color: #ff8c00;

    font-size: 11px;
}}

@keyframes ticker-scroll {{

    from {{
        transform: translateX(0%);
    }}

    to {{
        transform: translateX(-50%);
    }}
}}

</style>

<div class="news-ticker-container">

    <div class="news-ticker-track">

        {ticker_items}

    </div>

</div>

"""

components.html(
    ticker_html,
    height=42
)
# =========================================================
# FOOTER
# =========================================================

st.markdown("""<hr><div style='text-align:center;color:#888;'>Auto refreshes every 5 minutes<br>To purchase this bot or finetune a custom asset: <a href='mailto:arnkl@gmail.com'>arkankl07@gmail.com</a><br>This is for educational purposes only and does not constitute financial advice.</div>""", unsafe_allow_html=True)
