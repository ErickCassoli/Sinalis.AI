from typing import Tuple


def identificar_fonte(ativo: str) -> str:
    """Identifica a fonte de dados apropriada de acordo com o ativo."""
    ativo = ativo.upper()
    if "OTC" in ativo or ":" in ativo:
        return "iqoption"
    if ativo.endswith("USDT") or len(ativo) > 6:
        return "binance"
    return "iqoption"
