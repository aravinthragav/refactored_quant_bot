from telegram_sender import (
    send_photo
)

from trade_chart import (
    generate_trade_chart
)

from macro_calendar import (
    get_macro_risk
)

from db.signal_storage import (
    save_signal,
    signal_exists,
    generate_signal_hash
)

def process_signal(
    asset_name,
    config,
    df,
    pred_df,
    y_timestamp
):

    current_price = float(
        df['close'].iloc[-1]
    )

    forecast_price = float(
        pred_df['close'].iloc[-1]
    )

    move_pct = (
        (forecast_price - current_price)
        / current_price
    ) * 100

    direction = (
        "🟢 Bullish"
        if move_pct > 0
        else "🔴 Bearish"
    )

    atr = df['atr'].iloc[-1]

    if move_pct > 0:

        tp = forecast_price

        sl = (
            current_price
            - atr * config["atr_multiplier"]
        )

    else:

        tp = forecast_price

        sl = (
            current_price
            + atr * config["atr_multiplier"]
        )

    risk = abs(
        current_price - sl
    )

    reward = abs(
        tp - current_price
    )

    rr = (
        reward / risk
        if risk != 0
        else 0
    )

    if abs(move_pct) < config["signal_threshold"]:

        print("Move too small")

        return

    if rr < config["rr_min"]:

        print(f"Weak RR skipped: {rr:.2f}")

        return

    signal_hash = generate_signal_hash(
        config["ticker"],
        direction,
        forecast_price,
        str(y_timestamp.iloc[-1])
    )

    if signal_exists(signal_hash):

        print("Duplicate signal skipped")

        return

    macro = get_macro_risk()

    confidence = round(
        min(
            95,
            max(
                50,
                100 - (
                    df['volatility'].iloc[-1]
                    * 1000
                )
            )
        ) * macro["multiplier"],
        1
    )

    chart_path = generate_trade_chart(
        ticker=config["ticker"],
        df=df,
        pred_df=pred_df,
        current_price=current_price,
        tp=tp,
        sl=sl,
        direction=direction,
        rr=rr
    )

    message = f"""
🟡 {config['ticker']} AI Forecast

💰 Current:
{current_price:.2f}

🔮 Forecast:
{forecast_price:.2f}

📈 Move:
{move_pct:.2f}%

📊 Trend:
{direction}

⚖️ RR:
{rr:.2f}

🎯 Confidence:
{confidence:.1f}%

⚠️ Macro Risk:
{macro['risk']}

⏱ Horizon:
{config['pred_len'] * 5} mins
"""

    send_photo(
        chart_path,
        caption=message
    )

    save_signal(
        symbol=config["ticker"],
        timeframe=config["interval"],
        direction=direction,
        entry_price=current_price,
        tp_price=tp,
        sl_price=sl,
        forecast_price=forecast_price,
        move_pct=move_pct,
        confidence=confidence,
        macro_risk=macro["risk"],
        event_name="None"
    )

    print(
        f"{config['ticker']} signal sent"
    )