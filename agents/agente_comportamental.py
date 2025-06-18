import pandas as pd
from patterns import doji, martelo, engolfo_de_alta, engolfo_de_baixa


def avaliar(df: pd.DataFrame) -> dict | None:
    """Gera sinal baseado em padrões de candles simples."""
    ultimo = df.iloc[-1]
    anterior = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
    if martelo(ultimo):
        return {"sinal": "reversao", "motivo": "martelo"}
    if engolfo_de_alta(ultimo, anterior):
        return {"sinal": "alta", "motivo": "engolfo_alta"}
    if engolfo_de_baixa(ultimo, anterior):
        return {"sinal": "baixa", "motivo": "engolfo_baixa"}
    if doji(ultimo):
        return {"sinal": "indefinido", "motivo": "doji"}
    return None
