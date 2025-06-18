import pandas as pd


def gerar_sinal(candle: pd.Series, indicadores: dict, padroes: dict) -> str:
    """Decide o sinal final a partir de indicadores e padrões."""
    rsi = indicadores.get("rsi")
    if rsi is None:
        return "neutro"
    if rsi < 30 and padroes.get("engolfo_alta"):
        return "compra"
    if rsi > 70 and padroes.get("engolfo_baixa"):
        return "venda"
    return "neutro"
