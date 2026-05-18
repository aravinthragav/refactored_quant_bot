ASSETS = {

    "BTC": {

        "ticker": "BTC-USD",

        "interval": "5m",

        "lookback": 256,

        "pred_len": 12,

        "signal_threshold": 0.25,

        "atr_multiplier": 1.4,

        "rr_min": 1.5,

        "model_source": "huggingface",

        "model_name": "NeoQuasar/Kronos-small"
    },

    "GOLD": {

        "ticker": "XAUUSD=X",

        "interval": "5m",

        "lookback": 256,

        "pred_len": 12,

        "signal_threshold": 0.10,

        "atr_multiplier": 1.0,

        "rr_min": 1.3,

        "model_source": "local",

        "tokenizer_path": r"models/gold/tokenizer",

        "model_path": r"models/gold/model"
    }
}