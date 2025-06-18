from core.utils import identificar_fonte
from collectors import binance, iqoption
import pandas as pd


def coletar_dados(ativo: str, timeframe: str = "1m", limite: int = 1000) -> pd.DataFrame:
    """Coleta dados da fonte apropriada para o ativo."""
    fonte = identificar_fonte(ativo)
    if fonte == "binance":
        return binance.coletar_dados(ativo, timeframe, limite)
    # espaço para futuras integrações
    return iqoption.coletar_dados(ativo, timeframe, limite)
