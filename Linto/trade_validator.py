import datetime as dt
import traceback

import yfinance as yf
import pandas as pd

from db.signal_storage import (
    get_open_signals,
    update_signal_status
)

from telegram_sender import (
    send_message
)

# =========================================================
# VALIDATE OPEN SIGNALS
# =========================================================

def validate_open_signals():

    try:

        signals = get_open_signals()

        if len(signals) == 0:

            print(
                "No open trades."
            )

            return

        print(
            f"Validating {len(signals)} open trades..."
        )

        # =====================================================
        # LOOP SIGNALS
        # =====================================================

        for signal in signals:

            try:

                signal_id = signal["id"]

                ticker = signal["symbol"]

                direction = signal["direction"]

                entry = float(
                    signal["entry_price"]
                )

                tp = float(
                    signal["tp_price"]
                )

                sl = float(
                    signal["sl_price"]
                )

                rr = abs(
                    tp - entry
                ) / abs(
                    entry - sl
                )

                created_at = (
                    dt.datetime.fromisoformat(
                        signal["created_at"]
                    )
                )

                # =================================================
                # FORECAST EXPIRY
                # =================================================

                now_utc = dt.datetime.now(
                    dt.timezone.utc
                )

                elapsed_minutes = (
                    (
                        now_utc
                        - created_at
                    ).total_seconds()
                    / 60
                )

                # =================================================
                # DEFAULT:
                # 12 candles x 5m
                # = 60 mins
                # =================================================

                forecast_horizon_minutes = 60

                # =================================================
                # EXPIRE TRADE
                # =================================================

                if (
                    elapsed_minutes
                    > forecast_horizon_minutes
                ):

                    update_signal_status(

                        signal_id,

                        "EXPIRED",

                        0
                    )

                    print(
                        f"{ticker} expired."
                    )

                    continue

                # =================================================
                # FETCH LATEST DATA
                # =================================================

                df = yf.download(

                    ticker,

                    interval="5m",

                    period="1d",

                    progress=False
                )

                if df.empty:

                    continue

                # =================================================
                # FIX MULTIINDEX
                # =================================================

                if isinstance(
                    df.columns,
                    pd.MultiIndex
                ):

                    df.columns = (
                        df.columns
                        .get_level_values(0)
                    )

                # =================================================
                # LAST CANDLE
                # =================================================

                last_high = float(
                    df['High'].iloc[-1]
                )

                last_low = float(
                    df['Low'].iloc[-1]
                )

                # =================================================
                # LONG TRADES
                # =================================================

                if (
                    "Bullish"
                    in direction
                ):

                    # TP HIT
                    if last_high >= tp:

                        result_pct = (
                            (
                                tp - entry
                            )
                            / entry
                        ) * 100

                        update_signal_status(

                            signal_id,

                            "TP_HIT",

                            result_pct
                        )

                        message = f"""✅ TP HIT | {ticker}
📈 LONG
🎯 TP: {tp:.2f}
⚖️ RR: {rr:.2f}
💰 PnL: +{result_pct:.2f}%"""

                        send_message(
                            message
                        )

                        print(
                            f"{ticker} TP HIT"
                        )

                    # SL HIT
                    elif last_low <= sl:

                        result_pct = (
                            (
                                sl - entry
                            )
                            / entry
                        ) * 100

                        update_signal_status(

                            signal_id,

                            "SL_HIT",

                            result_pct
                        )

                        message = f"""❌ SL HIT | {ticker}
📈 LONG
🛑 SL: {sl:.2f}
⚖️ RR: {rr:.2f}
💰 PnL: {result_pct:.2f}%"""

                        send_message(
                            message
                        )

                        print(
                            f"{ticker} SL HIT"
                        )

                # =================================================
                # SHORT TRADES
                # =================================================

                else:

                    # TP HIT
                    if last_low <= tp:

                        result_pct = (
                            (
                                entry - tp
                            )
                            / entry
                        ) * 100

                        update_signal_status(

                            signal_id,

                            "TP_HIT",

                            result_pct
                        )

                        message = f"""✅ TP HIT | {ticker}
📉 SHORT
🎯 TP: {tp:.2f}
⚖️ RR: {rr:.2f}
💰 PnL: +{result_pct:.2f}%"""

                        send_message(
                            message
                        )

                        print(
                            f"{ticker} TP HIT"
                        )

                    # SL HIT
                    elif last_high >= sl:

                        result_pct = (
                            (
                                entry - sl
                            )
                            / entry
                        ) * 100

                        update_signal_status(

                            signal_id,

                            "SL_HIT",

                            result_pct
                        )

                        message = f"""❌ SL HIT | {ticker}
📉 SHORT
🛑 SL: {sl:.2f}
⚖️ RR: {rr:.2f}
💰 PnL: {result_pct:.2f}%"""

                        send_message(
                            message
                        )

                        print(
                            f"{ticker} SL HIT"
                        )

            except Exception:

                traceback.print_exc()

    except Exception:

        traceback.print_exc()