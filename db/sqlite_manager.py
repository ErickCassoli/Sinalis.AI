import sqlite3
from pathlib import Path
from typing import Iterable

from core import config

DB_PATH = Path(config.DB_PATH)


def conectar() -> sqlite3.Connection:
    """Abre conexão com o banco."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def criar_tabelas() -> None:
    """Cria tabelas de candles e sinais se não existirem."""
    conn = conectar()
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
    conn.close()


def salvar_candles(ativo: str, candles: Iterable[tuple]) -> None:
    """Insere candles no banco convertendo datas para texto."""
    conn = conectar()
    cur = conn.cursor()

    preparados = []
    for candle in candles:
        linha = list(candle)
        # garante que open_time seja uma string compatível com SQLite
        if hasattr(linha[1], "isoformat"):
            linha[1] = linha[1].isoformat()
        preparados.append(tuple(linha))

    cur.executemany(
        "INSERT INTO candles (ativo, open_time, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
        preparados,
    )
    conn.commit()
    conn.close()


def salvar_sinal(ativo: str, sinal: str, motivo: str) -> None:
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sinais (ativo, timestamp, sinal, motivo) VALUES (?, datetime('now'), ?, ?)",
        (ativo, sinal, motivo),
    )
    conn.commit()
    conn.close()
