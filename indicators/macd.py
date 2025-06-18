import pandas as pd
import ta


def adicionar_macd(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona colunas de MACD ao DataFrame."""
    df = df.copy()
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()
    return df
