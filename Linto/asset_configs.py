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

        "ticker": "GC=F",

        "interval": "5m",

        "lookback": 256,

        "pred_len": 12,

        "signal_threshold": 0.10,

        "atr_multiplier": 1.0,

        "rr_min": 1.3,

        "model_source": "local",

        "tokenizer_path": r"/teamspace/studios/this_studio/models/gold/tokenizer_base/best_model",

        "model_path": r"/teamspace/studios/this_studio/models/gold/basemodel_base/best_model"
    }
}