from __future__ import annotations

from datetime import datetime

import pandas as pd

from core.utils import identificar_fonte
from collectors import binance, iqoption


def coletar_dados(
    ativo: str,
    timeframe: str = "5m",
    limite: int = 1000,
    start_time: datetime | None = None,
) -> pd.DataFrame:
    """Roteia a coleta de dados para a API apropriada."""
    fonte = identificar_fonte(ativo)
    if fonte == "binance":
        return binance.coletar_dados(ativo.replace("-", ""), timeframe, limite, start_time)
    if fonte == "iqoption":
        return iqoption.coletar_dados(ativo, timeframe, limite, start_time)
    return pd.DataFrame()
