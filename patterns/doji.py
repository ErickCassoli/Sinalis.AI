import pandas as pd


def doji(candle: pd.Series) -> bool:
    """Retorna True se o candle for um doji."""
    corpo = abs(candle["close"] - candle["open"])
    sombra_total = candle["high"] - candle["low"]
    return corpo <= sombra_total * 0.1
