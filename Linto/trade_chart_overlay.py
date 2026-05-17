import matplotlib.pyplot as plt

def create_trade_overlay_chart(

    ax,

    entry,

    tp,

    sl,

    direction,

    rr
):


    if "Bullish" in direction:

        ax.axhspan(

            entry,

            tp,

            alpha=0.15,

            color='green'
        )

    else:

        ax.axhspan(

            tp,

            entry,

            alpha=0.15,

            color='green'
        )

    if "Bullish" in direction:

        ax.axhspan(

            sl,

            entry,

            alpha=0.15,

            color='red'
        )

    else:

        ax.axhspan(

            entry,

            sl,

            alpha=0.15,

            color='red'
        )

    ax.axhline(
        entry,
        color='white',
        linewidth=1.5
    )

    ax.axhline(
        tp,
        color='lime',
        linestyle='--',
        linewidth=2
    )

    ax.axhline(
        sl,
        color='red',
        linestyle='--',
        linewidth=2
    )

    label_x = 0.01

    ax.text(

        label_x,

        tp,

        f"TP {tp:.2f}",

        color='lime',

        fontsize=10,

        fontweight='bold'
    )

    ax.text(

        label_x,

        sl,

        f"SL {sl:.2f}",

        color='red',

        fontsize=10,

        fontweight='bold'
    )

    ax.text(

        label_x,

        entry,

        f"{direction} | RR {rr:.2f}",

        color='white',

        fontsize=11,

        fontweight='bold'
    )