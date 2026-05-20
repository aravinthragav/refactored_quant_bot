import time
import traceback
import subprocess
import sys

from asset_configs import ASSETS
from forecast_engine import process_asset
from trade_validator import validate_open_signals
from db.signal_storage import init_db
from monitoring import (
    send_alert,
    send_exception_alert
)
from session_scheduler import (
    send_session_briefings
)

init_db()

last_heartbeat = time.time()

    
dashboard_process = subprocess.Popen(
    [

    sys.executable,

       "-m",

        "streamlit",

       "run",

        "dashboard.py",

       "--server.headless=true",

       "--server.port=8501"

   ]

)

print(
   "Dashboard running at:"
)

print(
    "http://localhost:8501"
)

print("Multi Asset Quant Engine Started")

while True:

    try:
        validate_open_signals()

        for asset_name, config in ASSETS.items():

            try:

                print(f"Processing {asset_name}")
                send_session_briefings()

                process_asset(
                    asset_name,
                    config
                )

            except Exception as e:

                print(
                    f"{asset_name} failed:",
                    e
                )

                traceback.print_exc()

                send_alert(

                    f"{asset_name} FAILED",

                    str(e)
                )

                send_exception_alert(e)

                 # =====================================
        # HEARTBEAT
        # =====================================

        if (
            time.time()
            - last_heartbeat
        ) > 3600:

            send_alert(

                "BOT HEARTBEAT",

                "Bot running normally."
            )

            last_heartbeat = time.time()

    except Exception:

        traceback.print_exc()

    print("Sleeping 5 minutes...")

    time.sleep(300)