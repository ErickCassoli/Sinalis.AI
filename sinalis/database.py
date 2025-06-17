"""SQLite helper functions."""

from __future__ import annotations

import sqlite3
import pandas as pd
from .config import DB_NAME


def init_db() -> None:
    """Create database table if not exists."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS candles (
            open_time TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            interval TEXT NOT NULL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            pattern TEXT,
            signal TEXT,
            signal_reason TEXT,
            PRIMARY KEY (open_time, interval)
        )
        """
    )
    con.commit()
    con.close()


def store_data(df: pd.DataFrame) -> None:
    """Insert dataframe rows into database."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT OR REPLACE INTO candles (
                open_time, open, high, low, close, volume, interval,
                rsi, macd, macd_signal, macd_hist,
                bb_upper, bb_middle, bb_lower,
                pattern, signal, signal_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row['open_time'], row['open'], row['high'], row['low'],
                row['close'], row['volume'], row['interval'],
                row.get('rsi'), row.get('macd'), row.get('macd_signal'),
                row.get('macd_hist'), row.get('bb_upper'), row.get('bb_middle'),
                row.get('bb_lower'), row.get('pattern'), row.get('signal'),
                row.get('signal_reason')
            )
        )
    con.commit()
    con.close()
