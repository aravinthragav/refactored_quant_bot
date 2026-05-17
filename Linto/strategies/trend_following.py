def trend_following_filter(df):

    ema20 = (
        df['close']
        .rolling(20)
        .mean()
    )

    ema50 = (
        df['close']
        .rolling(50)
        .mean()
    )

    return (
        ema20.iloc[-1]
        > ema50.iloc[-1]
    )