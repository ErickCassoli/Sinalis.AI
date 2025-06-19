import pandas as pd
import requests
from datetime import datetime


def coletar_dados(
    ativo: str,
    timeframe: str = "1m",
    limite: int = 500,
    start_time: datetime | None = None,
) -> pd.DataFrame:
    """Coleta dados de candles da API da Binance."""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": ativo,
        "interval": timeframe,
        "limit": limite,
    }
    if start_time:
        params["startTime"] = int(start_time.timestamp() * 1000)
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ]
    df = pd.DataFrame(data, columns=cols)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)
    return df
