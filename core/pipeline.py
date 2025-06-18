import time
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import schedule

from collectors import coletor_universal
from db import database
from indicators.rsi import adicionar_rsi
from indicators.macd import adicionar_macd
from indicators.bollinger import adicionar_bbands
from patterns import engolfo_de_alta, engolfo_de_baixa
from agents import agente_decisao
from core import config

ATIVO = "BTCUSDT"
TIMEFRAME = "1h"
HISTORICO_MINIMO = 720  # 30 dias de candles de 1h


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(Path(config.DB_PATH))


def candle_existe(open_time: str) -> bool:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT 1 FROM candles WHERE ativo = ? AND open_time = ? LIMIT 1",
            (ATIVO, open_time),
        )
        return cur.fetchone() is not None


def contar_candles() -> int:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM candles WHERE ativo = ?",
            (ATIVO,),
        )
        return cur.fetchone()[0]


def salvar_candle_df(df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        open_time = row["open_time"].isoformat()
        if candle_existe(open_time):
            continue
        candle = (
            ATIVO,
            open_time,
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["volume"],
        )
        try:
            database.salvar_candle(candle)
        except Exception as exc:
            print("Erro ao salvar candle:", exc)


def carregar_historico_inicial() -> None:
    quantidade = contar_candles()
    if quantidade >= HISTORICO_MINIMO:
        return
    print("Carregando historico inicial de candles...")
    df = coletor_universal.coletar_dados(ATIVO, TIMEFRAME, HISTORICO_MINIMO)
    salvar_candle_df(df)
    print("Historico carregado. Total:", contar_candles())


def coletar_e_processar() -> None:
    try:
        df = coletor_universal.coletar_dados(ATIVO, TIMEFRAME, 2)
        if df.empty:
            print("Nenhum dado retornado da API")
            return
        now = datetime.utcnow()
        ultimo = df.iloc[-1]
        if ultimo["close_time"] > now:
            ultimo = df.iloc[-2]
        open_time = ultimo["open_time"].isoformat()
        if candle_existe(open_time):
            print("Candle ja existente:", open_time)
            return
        salvar_candle_df(pd.DataFrame([ultimo]))

        historico = database.buscar_candles(ATIVO, 200)
        cols = ["ativo", "open_time", "open", "high", "low", "close", "volume"]
        df_hist = pd.DataFrame(historico, columns=cols)
        df_hist["open_time"] = pd.to_datetime(df_hist["open_time"])
        novo = pd.DataFrame([
            {
                "ativo": ATIVO,
                "open_time": ultimo["open_time"],
                "open": ultimo["open"],
                "high": ultimo["high"],
                "low": ultimo["low"],
                "close": ultimo["close"],
                "volume": ultimo["volume"],
            }
        ])
        df_hist = pd.concat([df_hist, novo]).sort_values("open_time").reset_index(drop=True)

        df_ind = adicionar_rsi(adicionar_macd(adicionar_bbands(df_hist)))
        atual = df_ind.iloc[-1]
        anterior = df_ind.iloc[-2] if len(df_ind) > 1 else df_ind.iloc[-1]
        indicadores = {"rsi": atual["rsi"]}
        padroes = {
            "engolfo_alta": engolfo_de_alta(atual, anterior),
            "engolfo_baixa": engolfo_de_baixa(atual, anterior),
        }
        sinal = agente_decisao.gerar_sinal(atual, indicadores, padroes)
        if sinal != "neutro":
            database.salvar_sinal(ATIVO, sinal, "pipeline")
            print("Sinal gerado:", sinal)
        else:
            print("Sinal neutro")
    except Exception as exc:
        print("Erro no ciclo:", exc)


def iniciar() -> None:
    database.criar_tabelas()
    carregar_historico_inicial()
    schedule.every().hour.at(":01").do(coletar_e_processar)
    coletar_e_processar()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    iniciar()
