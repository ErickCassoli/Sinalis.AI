"""Main pipeline logic."""

from datetime import datetime
import time

from . import config
from .database import init_db, store_data
from .fetcher import get_binance_klines
from .indicators import add_indicators
from .patterns import detect_patterns
from .signals import classify_signals
from .risk import RiskManager


def process_interval(symbol: str, interval: str) -> None:
    df = get_binance_klines(symbol, interval)
    df = add_indicators(df)
    df = detect_patterns(df)
    df = classify_signals(df)
    store_data(df)
    for _, row in df.iterrows():
        if row["signal"] != "neutro":
            print(
                f"{row['open_time']} {interval}: {row['signal']} -> {row['signal_reason']}"
            )

def main() -> None:
    """Entry point for signal generation loop."""
    init_db()
    risk = RiskManager()
    while True:
        start = datetime.utcnow()
        try:
            for interval in config.INTERVALS:
                process_interval(config.SYMBOL, interval)
        except Exception as exc:
            print("Error processing:", exc)
        elapsed = (datetime.utcnow() - start).total_seconds()
        sleep_time = max(300 - elapsed, 0)
        time.sleep(sleep_time)
