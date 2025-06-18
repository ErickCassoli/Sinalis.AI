import sqlite3
from pathlib import Path
from core import config

DB_PATH = Path(config.DB_PATH)


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def criar_tabelas() -> None:
    """Cria tabelas de candles e sinais se necessário."""
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ativo TEXT,
                open_time TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS sinais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ativo TEXT,
                timestamp TEXT,
                sinal TEXT,
                motivo TEXT
            )"""
        )
        conn.commit()


def salvar_candle(candle: tuple) -> None:
    """Salva um candle no banco."""
    linha = list(candle)
    if hasattr(linha[1], "isoformat"):
        linha[1] = linha[1].isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO candles (ativo, open_time, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
            tuple(linha),
        )
        conn.commit()


def salvar_sinal(ativo: str, sinal: str, motivo: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO sinais (ativo, timestamp, sinal, motivo) VALUES (?, datetime('now'), ?, ?)",
            (ativo, sinal, motivo),
        )
        conn.commit()


def buscar_candles(ativo: str, limite: int = 100) -> list[tuple]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT ativo, open_time, open, high, low, close, volume FROM candles WHERE ativo = ? ORDER BY open_time DESC LIMIT ?",
            (ativo, limite),
        )
        return cur.fetchall()
