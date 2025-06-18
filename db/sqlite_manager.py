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
    conn = conectar()
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO candles (ativo, open_time, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
        candles,
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
