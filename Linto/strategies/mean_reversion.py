def mean_reversion_filter(df):

    rsi = df['rsi'].iloc[-1]

    return (
        rsi < 30
        or rsi > 70
    )