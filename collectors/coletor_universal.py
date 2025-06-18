from core.utils import identificar_fonte
from collectors import binance, iqoption
import requests
import pandas as pd


def coletar_dados(ativo, timeframe="5m", limite=1000, start_time=None):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": ativo,
        "interval": timeframe,
        "limit": limite
    }

    if start_time:
        params["startTime"] = int(pd.to_datetime(start_time).timestamp() * 1000)

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Erro na API da Binance:", response.text)
        return pd.DataFrame()

    data = response.json()
    candles = []
    for c in data:
        candles.append({
            "open_time": pd.to_datetime(c[0], unit="ms"),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
            "close_time": pd.to_datetime(c[6], unit="ms"),
        })

    return pd.DataFrame(candles)