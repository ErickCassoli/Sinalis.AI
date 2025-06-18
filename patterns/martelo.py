import pandas as pd


def martelo(candle: pd.Series) -> bool:
    """Detecta padrão de martelo simples."""
    corpo = abs(candle["close"] - candle["open"])
    sombra_inferior = min(candle["open"], candle["close"]) - candle["low"]
    sombra_superior = candle["high"] - max(candle["open"], candle["close"])
    return sombra_inferior > 2 * corpo and sombra_superior < corpo
