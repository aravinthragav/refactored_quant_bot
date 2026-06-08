import os

import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd

from trade_chart_overlay import (
    create_trade_overlay_chart
)

os.makedirs(
    "charts",
    exist_ok=True
)

def generate_trade_chart(
    ticker,
    df,
    pred_df,
    current_price,
    tp,
    sl,
    direction,
    rr
):

    chart_df = df.tail(120).copy()

    plot_df = chart_df.copy()

    plot_df = plot_df.set_index(
        pd.DatetimeIndex(
            plot_df['timestamps']
        )
    )

    plot_df = plot_df[
        [
            'open',
            'high',
            'low',
            'close',
            'volume'
        ]
    ]

    fig, axlist = mpf.plot(
        plot_df,
        type='candle',
        style='charles',
        volume=False,
        figsize=(16, 9),
        returnfig=True,
        title=f'{ticker} AI Forecast'
    )

    ax = axlist[0]

    ax.plot(
        range(len(chart_df)),
        chart_df['ema20'].values,
        color='cyan',
        linewidth=1.8,
        label='EMA 20'
    )

    ax.plot(
        range(len(chart_df)),
        chart_df['ema89_median'].values,
        color='purple',
        linewidth=2.5,
        label='EMA 89 Median'
    )

    create_trade_overlay_chart(
        ax=ax,
        entry=current_price,
        tp=tp,
        sl=sl,
        direction=direction,
        rr=rr
    )

    # Add www.aigoldforecast.com watermark in the middle
    ax.text(
        0.5, 0.5, 'www.aigoldforecast.com',
        transform=ax.transAxes,
        color='white',
        alpha=0.08,
        fontsize=44,
        fontweight='bold',
        rotation=15,
        ha='center',
        va='center',
        zorder=0
    )

    forecast_x = range(
        len(plot_df),
        len(plot_df) + len(pred_df)
    )

    last_close = (
        plot_df['close']
        .iloc[-1]
    )

    ax.plot(
        [len(plot_df) - 1, len(plot_df)],
        [last_close, pred_df['close'].iloc[0]],
        color='orange',
        linewidth=2
    )

    ax.plot(
        forecast_x,
        pred_df['close'].values,
        color='orange',
        linewidth=3
    )

    ax.legend(
        loc='upper left'
    )

    chart_path = f"charts/{ticker}.png"

    plt.savefig(
        chart_path,
        dpi=200,
        bbox_inches='tight'
    )

    plt.close(fig)

    return chart_path