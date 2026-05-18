import sqlite3
import hashlib
import datetime as dt
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_FILE = os.path.join(
    BASE_DIR,
    "signals.db"
)

def init_db():

    conn = sqlite3.connect(
        DB_FILE
    )

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS sent_signals (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            created_at TEXT,

            symbol TEXT,

            timeframe TEXT,

            direction TEXT,

            entry_price REAL,

            tp_price REAL,

            sl_price REAL,

            forecast_price REAL,

            move_pct REAL,

            confidence REAL,

            macro_risk TEXT,

            event_name TEXT,

            status TEXT DEFAULT 'OPEN',

            resolved_at TEXT,

            result_pct REAL,

            signal_hash TEXT UNIQUE
        )

    """)

    conn.commit()

    conn.close()

def generate_signal_hash(
    symbol,
    direction,
    forecast_price,
    forecast_timestamp
):

    raw = (
        f"{symbol}_"
        f"{direction}_"
        f"{forecast_price:.2f}_"
        f"{forecast_timestamp}"
    )

    return hashlib.md5(
        raw.encode()
    ).hexdigest()

def signal_exists(
    signal_hash
):

    conn = sqlite3.connect(
        DB_FILE
    )

    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM sent_signals
        WHERE signal_hash = ?
        ''',
        (signal_hash,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None

def save_signal(
    symbol,
    timeframe,
    direction,
    entry_price,
    tp_price,
    sl_price,
    forecast_price,
    move_pct,
    confidence,
    macro_risk,
    event_name
):

    conn = sqlite3.connect(
        DB_FILE
    )

    cursor = conn.cursor()

    signal_hash = generate_signal_hash(
        symbol,
        direction,
        forecast_price,
        dt.datetime.now().isoformat()
    )

    cursor.execute("""

        INSERT INTO sent_signals (

            created_at,

            symbol,

            timeframe,

            direction,

            entry_price,

            tp_price,

            sl_price,

            forecast_price,

            move_pct,

            confidence,

            macro_risk,

            event_name,

            signal_hash

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        dt.datetime.now(
            dt.timezone.utc
        ).isoformat(),

        symbol,

        timeframe,

        direction,

        entry_price,

        tp_price,

        sl_price,

        forecast_price,

        move_pct,

        confidence,

        macro_risk,

        event_name,

        signal_hash
    ))

    conn.commit()

    conn.close()

def recent_similar_signal_exists(

    symbol,

    direction,

    current_price,

    cooldown_minutes=60,

    price_threshold_pct=0.35
):

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM sent_signals

        WHERE symbol = ?

        AND direction = ?

        AND created_at >= datetime(
            'now',
            ?
        )

        ORDER BY id DESC

    """, (

        symbol,

        direction,

        f'-{cooldown_minutes} minutes'
    ))

    rows = cursor.fetchall()

    conn.close()

    for row in rows:

        old_price = row["entry_price"]

        distance_pct = abs(

            current_price
            - old_price

        ) / old_price * 100

        if (
            distance_pct
            <= price_threshold_pct
        ):

            return True

    return False

def get_open_signals():

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *
        FROM sent_signals
        WHERE status = 'OPEN'

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def update_signal_status(
    signal_id,
    status,
    result_pct
):

    conn = sqlite3.connect(
        DB_FILE
    )

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE sent_signals

        SET

            status = ?,

            resolved_at = ?,

            result_pct = ?

        WHERE id = ?

    """, (

        status,

        dt.datetime.now(
            dt.timezone.utc
        ).isoformat(),

        result_pct,

        signal_id
    ))

    conn.commit()

    conn.close()