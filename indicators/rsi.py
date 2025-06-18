import pandas as pd
import ta


def adicionar_rsi(df: pd.DataFrame, periodo: int = 14) -> pd.DataFrame:
    """Adiciona a coluna RSI ao DataFrame."""
    df = df.copy()
    df["rsi"] = ta.momentum.rsi(df["close"], window=periodo)
    return df
