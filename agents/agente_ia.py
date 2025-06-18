"""Agente de sinais baseado em modelo de IA."""

from pathlib import Path
from typing import Dict, Optional

import joblib
import pandas as pd

from indicators.rsi import adicionar_rsi
from indicators.macd import adicionar_macd
from indicators.bollinger import adicionar_bbands
from patterns.engolfo import engolfo_de_alta, engolfo_de_baixa

MODEL_PATH = Path("models/modelo_binario.pkl")
SCALER_PATH = Path("models/escalador.pkl")

_FEATURES = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "rsi",
    "macd",
    "macd_signal",
    "macd_diff",
    "bb_high",
    "bb_low",
    "engolfo_alta",
    "engolfo_baixa",
]

_model = None
_scaler = None


def _carregar_modelo() -> None:
    """Carrega modelo e escalador se ainda não estiverem na memória."""
    global _model, _scaler
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    if _scaler is None and SCALER_PATH.exists():
        _scaler = joblib.load(SCALER_PATH)


def _preparar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Gera indicadores e colunas usadas pelo modelo."""
    df = adicionar_rsi(adicionar_macd(adicionar_bbands(df)))
    df = df.copy()
    df["engolfo_alta"] = False
    df["engolfo_baixa"] = False
    for i in range(1, len(df)):
        df.loc[df.index[i], "engolfo_alta"] = engolfo_de_alta(df.iloc[i], df.iloc[i - 1])
        df.loc[df.index[i], "engolfo_baixa"] = engolfo_de_baixa(df.iloc[i], df.iloc[i - 1])
    return df


def gerar_sinal_ia(df: pd.DataFrame) -> Optional[Dict[str, float]]:
    """Retorna sinal CALL/PUT a partir de um DataFrame com candles."""
    _carregar_modelo()
    if _model is None:
        return None
    df = _preparar_features(df)
    amostra = df.iloc[-1:][_FEATURES]
    if _scaler is not None:
        amostra = pd.DataFrame(_scaler.transform(amostra), columns=amostra.columns)
    probas = _model.predict_proba(amostra.values)[0]
    pred = int(probas[1] >= probas[0])
    sinal = "CALL" if pred == 1 else "PUT"
    confianca = float(probas[pred])
    return {"sinal": sinal, "confianca": confianca, "motivo": "Modelo IA"}