import time
import pandas as pd
from collectors import binance, iqoption
from core import config
from core.utils import identificar_fonte
from agents import agente_tecnico, agente_comportamental, agente_validacao, agente_risco
from db import sqlite_manager


def ciclo(ativo: str, perdas: int = 0) -> None:
    fonte = identificar_fonte(ativo)
    if fonte == "binance":
        df = binance.coletar_dados(ativo, config.TIMEFRAME, 100)
    else:
        df = iqoption.coletar_dados(ativo, config.TIMEFRAME, 100)

    sinais = [
        agente_tecnico.avaliar(df),
        agente_comportamental.avaliar(df),
    ]
    sinal_final = agente_validacao.validar(sinais)
    sinal_final = agente_risco.aplicar_gerenciamento(sinal_final, perdas)

    candles_to_save = df[["open_time", "open", "high", "low", "close", "volume"]]
    sqlite_manager.salvar_candles(ativo, [tuple([ativo] + list(row)) for row in candles_to_save.values])
    if sinal_final:
        sqlite_manager.salvar_sinal(ativo, sinal_final["sinal"], sinal_final["motivo"])
        print(time.ctime(), sinal_final)


def iniciar() -> None:
    sqlite_manager.criar_tabelas()
    while True:
        ciclo(config.ATIVO_PADRAO)
        time.sleep(300)
