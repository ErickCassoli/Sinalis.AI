import pandas as pd
from indicators.rsi import adicionar_rsi
from indicators.bollinger import adicionar_bbands


def avaliar(df: pd.DataFrame) -> dict | None:
    """Gera sinal baseado em RSI e Bandas de Bollinger."""
    df = adicionar_rsi(adicionar_bbands(df))
    ultimo = df.iloc[-1]
    if ultimo["rsi"] < 30 and ultimo["close"] < ultimo["bb_low"]:
        return {"sinal": "compra", "motivo": "rsi_bb"}
    if ultimo["rsi"] > 70 and ultimo["close"] > ultimo["bb_high"]:
        return {"sinal": "venda", "motivo": "rsi_bb"}
    return None
