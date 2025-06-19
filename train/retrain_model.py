from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from db import database
from agents import agente_ia

MODEL_OUT = Path("models/modelo_atualizado.pkl")


def carregar_dataset():
    sinais = database.buscar_sinais_com_resultado()
    if not sinais:
        return pd.DataFrame(), []

    registros = []
    targets = []
    for s in sinais:
        candle = database.buscar_candle_por_tempo(s["ativo"], s["candle_time"])
        if candle is None:
            continue
        historico = database.buscar_candles(s["ativo"], 200)
        cols = ["ativo", "open_time", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(historico, columns=cols)
        df["open_time"] = pd.to_datetime(df["open_time"])
        df = df.sort_values("open_time")
        df_feat = agente_ia._preparar_features(df)
        linha = df_feat[df_feat["open_time"] == candle["open_time"]]
        if linha.empty:
            continue
        registros.append(linha[agente_ia._FEATURES].iloc[0].values)
        targets.append(1 if s["resultado"] == "WIN" else 0)
    if not registros:
        return pd.DataFrame(), []
    X = pd.DataFrame(registros, columns=agente_ia._FEATURES)
    return X, targets


def main() -> None:
    X, y = carregar_dataset()
    if X.empty:
        print("Nenhum dado para re-treinamento.")
        return
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    MODEL_OUT.parent.mkdir(exist_ok=True, parents=True)
    joblib.dump(model, MODEL_OUT)
    print(f"Modelo salvo em {MODEL_OUT}")


if __name__ == "__main__":
    main()
