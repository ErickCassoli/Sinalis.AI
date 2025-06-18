import pandas as pd


def engolfo_de_alta(atual: pd.Series, anterior: pd.Series) -> bool:
    """Verifica engolfo de alta."""
    return (
        atual["close"] > atual["open"]
        and anterior["close"] < anterior["open"]
        and atual["open"] < anterior["close"]
        and atual["close"] > anterior["open"]
    )


def engolfo_de_baixa(atual: pd.Series, anterior: pd.Series) -> bool:
    """Verifica engolfo de baixa."""
    return (
        atual["close"] < atual["open"]
        and anterior["close"] > anterior["open"]
        and atual["open"] > anterior["close"]
        and atual["close"] < anterior["open"]
    )
