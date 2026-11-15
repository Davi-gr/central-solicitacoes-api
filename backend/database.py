import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "central.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS solicitacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                categoria TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Aberta',
                criado_em TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def criar_solicitacao(dados):
    criado_em = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO solicitacoes
                (titulo, descricao, categoria, prioridade, status, criado_em)
            VALUES (?, ?, ?, ?, 'Aberta', ?)
            """,
            (dados.titulo, dados.descricao, dados.categoria, dados.prioridade, criado_em),
        )
        conn.commit()
        linha = conn.execute(
            "SELECT * FROM solicitacoes WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(linha)
    finally:
        conn.close()


def listar_solicitacoes(status=None, prioridade=None):
    condicoes = []
    parametros = []

    if status is not None:
        condicoes.append("status = ?")
        parametros.append(status)
    if prioridade is not None:
        condicoes.append("prioridade = ?")
        parametros.append(prioridade)

    sql = "SELECT * FROM solicitacoes"
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += " ORDER BY id DESC"

    conn = get_connection()
    try:
        linhas = conn.execute(sql, parametros).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        conn.close()


def buscar_solicitacao(id):
    conn = get_connection()
    try:
        linha = conn.execute(
            "SELECT * FROM solicitacoes WHERE id = ?", (id,)
        ).fetchone()
        return dict(linha) if linha else None
    finally:
        conn.close()