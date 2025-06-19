from __future__ import annotations

from typing import Dict

import pandas as pd

from core.config import (
    MODO_OPERACAO,
    EXPIRACAO_CANDLES,
    STOP_LOSS_PERCENT,
    TAKE_PROFIT_PERCENT,
)


def avaliar_resultado_sinal(sinal: Dict, df_candles: pd.DataFrame) -> str:
    """Avalia se um sinal resultou em WIN ou LOSS."""
    direcao = sinal.get("sinal", "").upper()

    if df_candles.empty:
        return "LOSS"

    if MODO_OPERACAO == "opcao_binaria":
        expiracao = int(sinal.get("expiracao", EXPIRACAO_CANDLES))
        if len(df_candles) <= expiracao:
            return "LOSS"
        entrada = df_candles.iloc[0]["close"]
        saida = df_candles.iloc[expiracao]["close"]
        if direcao in {"CALL", "COMPRA", "ALTA"}:
            return "WIN" if saida > entrada else "LOSS"
        else:
            return "WIN" if saida < entrada else "LOSS"

    # daytrade
    entrada = df_candles.iloc[0]["close"]
    tp_percent = float(sinal.get("tp", TAKE_PROFIT_PERCENT))
    sl_percent = float(sinal.get("sl", STOP_LOSS_PERCENT))

    if direcao in {"CALL", "COMPRA", "ALTA"}:
        tp = entrada * (1 + tp_percent)
        sl = entrada * (1 - sl_percent)
        for _, candle in df_candles.iloc[1:].iterrows():
            if candle["high"] >= tp:
                return "WIN"
            if candle["low"] <= sl:
                return "LOSS"
        return "WIN" if df_candles.iloc[-1]["close"] > entrada else "LOSS"
    else:
        tp = entrada * (1 - tp_percent)
        sl = entrada * (1 + sl_percent)
        for _, candle in df_candles.iloc[1:].iterrows():
            if candle["low"] <= tp:
                return "WIN"
            if candle["high"] >= sl:
                return "LOSS"
        return "WIN" if df_candles.iloc[-1]["close"] < entrada else "LOSS"
