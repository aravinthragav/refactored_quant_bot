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
    generate_signal_hash,
    recent_similar_signal_exists
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

    forecast_delta = forecast_price - current_price

    if move_pct > 0:

        tp = current_price + (forecast_delta * 0.75)

        sl = (
            current_price
            - atr * config["atr_multiplier"]
        )

    else:

        tp = current_price + (forecast_delta * 0.75)

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

    try:
        pred_len = config["pred_len"]
        actual = df['close'].tail(pred_len).values
        predicted = pred_df['close'].values[:len(actual)]
        mae = float(sum(abs(actual - predicted)) / len(actual))
    except:
        mae = 0.0

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

    message = f"""🟡 {config['ticker']} AI Forecast

💰 Current: {current_price:.2f}
🔮 Forecast: {forecast_price:.2f}
📈 Move: {move_pct:.2f}%
📊 Trend: {direction}
⚖️ RR: {rr:.2f}
🎯 Model MAE: {mae:.2f}
⚠️ Macro Risk: {macro['risk']}
⏱ Horizon: {config['pred_len'] * 5} mins"""
    
    clustered = recent_similar_signal_exists(

        symbol=config["ticker"],

        direction=direction,

        current_price=current_price,

        cooldown_minutes=90,

        price_threshold_pct=0.5
    )

    if clustered:

        print(
            "Clustered signal skipped"
        )

        return

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
        confidence=mae,
        macro_risk=macro["risk"],
        event_name="None"
    )

    print(
        f"{config['ticker']} signal sent"
    )