"""Candle pattern detection."""

import pandas as pd


def detect_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect simple candle patterns."""
    patterns = []
    for i in range(len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1] if i > 0 else row
        body = row["close"] - row["open"]
        prev_body = prev["close"] - prev["open"]
        range_ = row["high"] - row["low"]
        upper = row["high"] - max(row["open"], row["close"])
        lower = min(row["open"], row["close"]) - row["low"]

        pat = []
        if body > 0 and prev_body < 0 and row["open"] < prev["close"] and row["close"] > prev["open"]:
            pat.append("bullish_engulfing")
        if body < 0 and prev_body > 0 and row["open"] > prev["close"] and row["close"] < prev["open"]:
            pat.append("bearish_engulfing")
        if abs(body) <= 0.1 * range_:
            pat.append("doji")
        if lower > 2 * abs(body) and upper <= abs(body):
            pat.append("hammer")
        patterns.append(",".join(pat))
    df["pattern"] = patterns
    return df
