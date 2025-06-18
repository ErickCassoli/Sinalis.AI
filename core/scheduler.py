import time
import schedule
from collectors import coletor_universal
from indicators.rsi import adicionar_rsi
from indicators.macd import adicionar_macd
from indicators.bollinger import adicionar_bbands
from patterns import engolfo_de_alta, engolfo_de_baixa
from agents import agente_decisao
from db import database
from core import config


def executar_ciclo(ativo: str = config.ATIVO_PADRAO) -> None:
    """Executa uma etapa completa de coleta e geração de sinal."""
    df = coletor_universal.coletar_dados(ativo, config.TIMEFRAME, 100)
    if df.empty:
        return
    df = adicionar_rsi(adicionar_macd(adicionar_bbands(df)))
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
    indicadores = {"rsi": ultimo["rsi"]}
    padroes = {
        "engolfo_alta": engolfo_de_alta(ultimo, penultimo),
        "engolfo_baixa": engolfo_de_baixa(ultimo, penultimo),
    }
    sinal = agente_decisao.gerar_sinal(ultimo, indicadores, padroes)
    database.salvar_candle(
        (
            ativo,
            ultimo["open_time"],
            ultimo["open"],
            ultimo["high"],
            ultimo["low"],
            ultimo["close"],
            ultimo["volume"],
        )
    )
    if sinal != "neutro":
        database.salvar_sinal(ativo, sinal, "decisao_base")
    print(time.ctime(), sinal)


def iniciar() -> None:
    database.criar_tabelas()
    schedule.every(5).minutes.do(executar_ciclo)
    executar_ciclo()
    while True:
        schedule.run_pending()
        time.sleep(1)
