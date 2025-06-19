import sqlite3
from pathlib import Path
from typing import Optional
from core import config

DB_PATH = Path(config.DB_PATH)


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _add_column_if_not_exists(conn: sqlite3.Connection, table: str, column_def: str) -> None:
    """Adiciona coluna se ela não existir na tabela."""
    col_name = column_def.split()[0]
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cur.fetchall()}
    if col_name not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")


def criar_tabelas() -> None:
    """Cria ou atualiza tabelas de candles e sinais."""
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
                candle_time TEXT,
                sinal TEXT,
                motivo TEXT,
                modo TEXT,
                expiracao INTEGER,
                tp REAL,
                sl REAL,
                confianca REAL,
                resultado TEXT
            )"""
        )

        # migrações de colunas caso o banco seja antigo
        _add_column_if_not_exists(conn, "sinais", "candle_time TEXT")
        _add_column_if_not_exists(conn, "sinais", "modo TEXT")
        _add_column_if_not_exists(conn, "sinais", "expiracao INTEGER")
        _add_column_if_not_exists(conn, "sinais", "tp REAL")
        _add_column_if_not_exists(conn, "sinais", "sl REAL")
        _add_column_if_not_exists(conn, "sinais", "confianca REAL")
        _add_column_if_not_exists(conn, "sinais", "resultado TEXT")

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


def salvar_sinal(
    ativo: str,
    sinal: str,
    motivo: str,
    modo: str,
    expiracao: Optional[int],
    tp: Optional[float],
    sl: Optional[float],
    confianca: Optional[float],
    candle_time: str,
) -> None:
    with _conn() as conn:
        conn.execute(
            (
                "INSERT INTO sinais (ativo, timestamp, candle_time, sinal, motivo, modo, expiracao, tp, sl, confianca) "
                "VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            (ativo, candle_time, sinal, motivo, modo, expiracao, tp, sl, confianca),
        )
        conn.commit()


def atualizar_resultado(sinal_id: int, resultado: str) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE sinais SET resultado = ? WHERE id = ?",
            (resultado, sinal_id),
        )
        conn.commit()


def buscar_candles(ativo: str, limite: int = 100) -> list[tuple]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT ativo, open_time, open, high, low, close, volume FROM candles WHERE ativo = ? ORDER BY open_time DESC LIMIT ?",
            (ativo, limite),
        )
        return cur.fetchall()


def buscar_candle_por_tempo(ativo: str, open_time: str) -> Optional[sqlite3.Row]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM candles WHERE ativo = ? AND open_time = ? LIMIT 1",
            (ativo, open_time),
        )
        return cur.fetchone()


def buscar_sinais_sem_resultado() -> list[sqlite3.Row]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM sinais WHERE resultado IS NULL"
        )
        return cur.fetchall()


def buscar_sinais_com_resultado() -> list[sqlite3.Row]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM sinais WHERE resultado IN ('WIN', 'LOSS')"
        )
        return cur.fetchall()
