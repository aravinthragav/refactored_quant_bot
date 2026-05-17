import sqlite3

from .signal_storage import DB_FILE

def get_win_rate():

    conn = sqlite3.connect(
        DB_FILE
    )

    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM sent_signals
        WHERE status='TP_HIT'
        '''
    )

    wins = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM sent_signals
        WHERE status IN ('TP_HIT', 'SL_HIT')
        '''
    )

    total = cursor.fetchone()[0]

    conn.close()

    if total == 0:

        return 0

    return (
        wins / total
    ) * 100