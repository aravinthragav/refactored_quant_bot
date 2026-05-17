def breakout_filter(df):

    recent_high = (
        df['high']
        .tail(20)
        .max()
    )

    current = (
        df['close']
        .iloc[-1]
    )

    return (
        current >= recent_high
    )