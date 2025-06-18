from core import config


def aplicar_gerenciamento(sinal: dict | None, perdas: int) -> dict | None:
    """Aplica regras básicas de risco como stop diário."""
    if sinal is None:
        return None
    if perdas >= config.STOP_DIARIO:
        return {"sinal": "parar", "motivo": "stop_diario"}
    return sinal
