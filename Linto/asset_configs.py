ASSETS = {

    "BTC": {

        "ticker": "BTC-USD",

        "asset_type": "crypto",

        "interval": "5m",

        "lookback": 256,

        "pred_len": 12,

        "signal_threshold": 0.20,

        "atr_multiplier": 1.2,

        "rr_min": 1.5,

        "macro_sensitive": True
    },

    "GOLD": {

        "ticker": "XAUUSD=X",

        "asset_type": "commodity",

        "interval": "5m",

        "lookback": 256,

        "pred_len": 12,

        "signal_threshold": 0.10,

        "atr_multiplier": 1.0,

        "rr_min": 1.3,

        "macro_sensitive": True
    }
}