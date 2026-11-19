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


def listar_solicitacoes(status=None, prioridade=None, busca=None):
    condicoes = []
    parametros = []

    if status is not None:
        condicoes.append("status = ?")
        parametros.append(status)
    if prioridade is not None:
        condicoes.append("prioridade = ?")
        parametros.append(prioridade)
    if busca:
        condicoes.append("(titulo LIKE ? OR descricao LIKE ?)")
        parametros.extend((f"%{busca}%", f"%{busca}%"))

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



def buscar_solicitacao(solicitacao_id):
    conn = get_connection()
    try:
        linha = conn.execute(
            "SELECT * FROM solicitacoes WHERE id = ?", (solicitacao_id,)
        ).fetchone()
        return dict(linha) if linha else None
    finally:
        conn.close()

def atualizar_status(solicitacao_id, status_atual, novo_status):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE solicitacoes SET status = ? WHERE id = ? AND status = ?",
            (novo_status, solicitacao_id, status_atual),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None  # ninguém foi alterado: o status mudou no meio do caminho
        linha = conn.execute(
            "SELECT * FROM solicitacoes WHERE id = ?", (solicitacao_id,)
        ).fetchone()
        return dict(linha)
    finally:
        conn.close()

def resumo_por_status():
    conn = get_connection()
    try:
        linhas = conn.execute(
            "SELECT status, COUNT(*) AS quantidade FROM solicitacoes GROUP BY status"
        ).fetchall()
        por_status = {linha["status"]: linha["quantidade"] for linha in linhas}
        return {"total": sum(por_status.values()), "por_status": por_status}
    finally:
        conn.close()