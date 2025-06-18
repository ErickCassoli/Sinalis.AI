import pandas as pd


def detectar_doji(df: pd.DataFrame) -> pd.DataFrame:
    """Marca candles do tipo doji."""
    df = df.copy()
    df["doji"] = (df["close"] - df["open"]).abs() <= (df["high"] - df["low"]) * 0.1
    return df


def detectar_martelo(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta padrão de martelo simples."""
    df = df.copy()
    corpo = (df["close"] - df["open"]).abs()
    sombra_inferior = df[["open", "close"]].min(axis=1) - df["low"]
    sombra_superior = df["high"] - df[["open", "close"]].max(axis=1)
    df["martelo"] = (sombra_inferior > 2 * corpo) & (sombra_superior < corpo)
    return df

def detectar_engolfo(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta engolfo de alta ou baixa."""
    df = df.copy()
    engolfo_alta = (
        (df['close'] > df['open']) &
        (df['close'].shift(1) < df['open'].shift(1)) &
        (df['open'] < df['close'].shift(1)) &
        (df['close'] > df['open'].shift(1))
    )
    engolfo_baixa = (
        (df['close'] < df['open']) &
        (df['close'].shift(1) > df['open'].shift(1)) &
        (df['open'] > df['close'].shift(1)) &
        (df['close'] < df['open'].shift(1))
    )
    df['engolfo_alta'] = engolfo_alta
    df['engolfo_baixa'] = engolfo_baixa
    return df
