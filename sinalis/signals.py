"""Signal classification."""

import pandas as pd


def classify_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Classify candles as buy, sell or neutral."""
    signals = []
    reasons = []
    for _, row in df.iterrows():
        sig = "neutro"
        reason = ""
        if row["rsi"] < 30 and "bullish_engulfing" in row["pattern"]:
            sig = "compra"
            reason = "RSI < 30 + Engolfo de Alta"
        elif row["rsi"] > 70 and "bearish_engulfing" in row["pattern"]:
            sig = "venda"
            reason = "RSI > 70 + Engolfo de Baixa"
        signals.append(sig)
        reasons.append(reason)
    df["signal"] = signals
    df["signal_reason"] = reasons
    return df
