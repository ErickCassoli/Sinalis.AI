import pandas as pd
from patterns.candles import detectar_doji, detectar_martelo, detectar_engolfo


def avaliar(df: pd.DataFrame) -> dict | None:
    """Gera sinal baseado em padrões de candles."""
    df = detectar_doji(detectar_martelo(detectar_engolfo(df)))
    ultimo = df.iloc[-1]
    if ultimo.get("martelo"):
        return {"sinal": "reversao", "motivo": "martelo"}
    if ultimo.get("engolfo_alta"):
        return {"sinal": "alta", "motivo": "engolfo_alta"}
    if ultimo.get("engolfo_baixa"):
        return {"sinal": "baixa", "motivo": "engolfo_baixa"}
    if ultimo.get("doji"):
        return {"sinal": "indefinido", "motivo": "doji"}
    return None
