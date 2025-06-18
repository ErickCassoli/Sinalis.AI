from typing import Iterable, Optional


def validar(sinais: Iterable[dict]) -> Optional[dict]:
    """Confirma sinal quando múltiplos agentes concordam."""
    sinais = [s for s in sinais if s]
    if not sinais:
        return None
    tipos = {s['sinal'] for s in sinais}
    if len(tipos) == 1:
        return {"sinal": tipos.pop(), "motivo": "confirmado", "agentes": len(sinais)}
    return None
