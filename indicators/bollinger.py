import pandas as pd
import ta


def adicionar_bbands(df: pd.DataFrame, janela: int = 20) -> pd.DataFrame:
    """Adiciona Bandas de Bollinger ao DataFrame."""
    df = df.copy()
    bb = ta.volatility.BollingerBands(df["close"], window=janela)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()
    return df
