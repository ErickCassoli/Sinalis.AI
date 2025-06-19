import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import schedule

from collectors import coletor_universal
from db import database
from indicators.rsi import adicionar_rsi
from indicators.macd import adicionar_macd
from indicators.bollinger import adicionar_bbands
from patterns import engolfo_de_alta, engolfo_de_baixa
from agents import agente_decisao, agente_ia
from core import config
from estrategias.avaliar_resultado import avaliar_resultado_sinal

ATIVO = config.ATIVO_PADRAO
TIMEFRAME = config.TIMEFRAME
TIMER = "30s"
HISTORICO_MINIMO = 8640  # 30 dias de candles de 5 minutos


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
            "SELECT COUNT(*) FROM candles WHERE ativo = ?", (ATIVO,)
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
        print("✅ Histórico suficiente já existente.")
        return

    print("⏳ Carregando histórico inicial paginado de candles...")

    df_total = pd.DataFrame()
    agora = datetime.utcnow()
    minutos = 30 * 24 * 60  # 30 dias em minutos
    delta = timedelta(minutes=5 * 1000)  # a cada 1000 candles de 5m = ~3 dias e 11h
    inicio = agora - timedelta(minutes=minutos)

    while inicio < agora:
        fim = inicio + delta
        print(f"🔄 Coletando de {inicio} até {fim}...")
        df = coletor_universal.coletar_dados(ATIVO, TIMEFRAME, 1000, start_time=inicio)
        if df.empty:
            print("⚠️ Nenhum dado retornado, parando a coleta.")
            break
        salvar_candle_df(df)
        df_total = pd.concat([df_total, df])
        ultimo_time = df["open_time"].max()
        inicio = ultimo_time + timedelta(minutes=5)

    print(f"✅ Histórico carregado. Total inserido: {len(df_total)}")
    print("📊 Total atual no banco:", contar_candles())



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
            print("Candle já existente:", open_time)
            return

        salvar_candle_df(pd.DataFrame([ultimo]))

        historico = database.buscar_candles(ATIVO, 500)
        cols = ["ativo", "open_time", "open", "high", "low", "close", "volume"]
        df_hist = pd.DataFrame(historico, columns=cols)
        df_hist["open_time"] = pd.to_datetime(df_hist["open_time"])
        novo = pd.DataFrame([{
            "ativo": ATIVO,
            "open_time": ultimo["open_time"],
            "open": ultimo["open"],
            "high": ultimo["high"],
            "low": ultimo["low"],
            "close": ultimo["close"],
            "volume": ultimo["volume"],
        }])
        df_hist = pd.concat([df_hist, novo]).sort_values("open_time").reset_index(drop=True)

        df_ind = adicionar_rsi(adicionar_macd(adicionar_bbands(df_hist)))
        atual = df_ind.iloc[-1]
        anterior = df_ind.iloc[-2] if len(df_ind) > 1 else df_ind.iloc[-1]
        indicadores = {"rsi": atual["rsi"]}
        padroes = {
            "engolfo_alta": engolfo_de_alta(atual, anterior),
            "engolfo_baixa": engolfo_de_baixa(atual, anterior),
        }
        sinal_ia = agente_ia.gerar_sinal_ia(df_hist)
        if sinal_ia:
            database.salvar_sinal(
                ATIVO,
                sinal_ia["sinal"],
                sinal_ia["motivo"],
                config.MODO_OPERACAO,
                config.EXPIRACAO_CANDLES if config.MODO_OPERACAO == "opcao_binaria" else None,
                config.TAKE_PROFIT_PERCENT if config.MODO_OPERACAO == "daytrade" else None,
                config.STOP_LOSS_PERCENT if config.MODO_OPERACAO == "daytrade" else None,
                sinal_ia.get("confianca"),
                open_time,
            )
            print("✅ Sinal IA:", sinal_ia)
        else:
            sinal = agente_decisao.gerar_sinal(atual, indicadores, padroes)
            if sinal != "neutro":
                database.salvar_sinal(
                    ATIVO,
                    sinal,
                    "pipeline",
                    config.MODO_OPERACAO,
                    config.EXPIRACAO_CANDLES if config.MODO_OPERACAO == "opcao_binaria" else None,
                    config.TAKE_PROFIT_PERCENT if config.MODO_OPERACAO == "daytrade" else None,
                    config.STOP_LOSS_PERCENT if config.MODO_OPERACAO == "daytrade" else None,
                    None,
                    open_time,
                )
                print("✅ Sinal gerado:", sinal)
            else:
                print("Sinal neutro")

        # Avalia sinais pendentes
        sinais_pendentes = database.buscar_sinais_sem_resultado()
        for s in sinais_pendentes:
            if s["ativo"] != ATIVO:
                continue
            df_future = df_hist[df_hist["open_time"] >= pd.to_datetime(s["candle_time"])]
            resultado = avaliar_resultado_sinal(dict(s), df_future.reset_index(drop=True))
            database.atualizar_resultado(s["id"], resultado)
    except Exception as exc:
        print("❌ Erro no ciclo:", exc)


def iniciar_schedule():
    print(f"⏱️ Iniciando agendamento a cada {TIMER}...")
    schedule.every(30).seconds.do(coletar_e_processar)
    coletar_e_processar()  # roda a primeira vez já
    while True:
        schedule.run_pending()
        time.sleep(1)


def iniciar():
    print("🚀 Iniciando pipeline...")
    database.criar_tabelas()
    carregar_historico_inicial()
    iniciar_schedule()


if __name__ == "__main__":
    iniciar()
