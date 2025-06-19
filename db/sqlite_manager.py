import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from core import config

DB_PATH = Path(config.DB_PATH)


def conectar() -> sqlite3.Connection:
    """Abre conexão com o banco."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def _add_column_if_not_exists(conn: sqlite3.Connection, table: str, column_def: str) -> None:
    col_name = column_def.split()[0]
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cur.fetchall()}
    if col_name not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")


def criar_tabelas() -> None:
    """Cria ou atualiza tabelas de candles e sinais."""
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

    _add_column_if_not_exists(conn, "sinais", "candle_time TEXT")
    _add_column_if_not_exists(conn, "sinais", "modo TEXT")
    _add_column_if_not_exists(conn, "sinais", "expiracao INTEGER")
    _add_column_if_not_exists(conn, "sinais", "tp REAL")
    _add_column_if_not_exists(conn, "sinais", "sl REAL")
    _add_column_if_not_exists(conn, "sinais", "confianca REAL")
    _add_column_if_not_exists(conn, "sinais", "resultado TEXT")

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
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        (
            "INSERT INTO sinais (ativo, timestamp, candle_time, sinal, motivo, modo, expiracao, tp, sl, confianca) "
            "VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)"
        ),
        (ativo, candle_time, sinal, motivo, modo, expiracao, tp, sl, confianca),
    )
    conn.commit()
    conn.close()


def atualizar_resultado(sinal_id: int, resultado: str) -> None:
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "UPDATE sinais SET resultado = ? WHERE id = ?",
        (resultado, sinal_id),
    )
    conn.commit()
    conn.close()


def buscar_sinais_sem_resultado() -> list[sqlite3.Row]:
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM sinais WHERE resultado IS NULL")
    rows = cur.fetchall()
    conn.close()
    return rows


def buscar_sinais_com_resultado() -> list[sqlite3.Row]:
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM sinais WHERE resultado IN ('WIN', 'LOSS')")
    rows = cur.fetchall()
    conn.close()
    return rows


def buscar_candle_por_tempo(ativo: str, open_time: str) -> Optional[sqlite3.Row]:
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM candles WHERE ativo = ? AND open_time = ? LIMIT 1",
        (ativo, open_time),
    )
    row = cur.fetchone()
    conn.close()
    return row
