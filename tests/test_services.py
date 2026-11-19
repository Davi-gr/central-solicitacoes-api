import pytest
from types import SimpleNamespace

from backend import database
from backend.services import TransicaoInvalidaError, validar_transicao


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    banco = tmp_path / "central.db"
    monkeypatch.setattr(database, "DB_PATH", banco)
    database.init_db()
    return banco


def adicionar_solicitacao(titulo, descricao, categoria="Teste",
                          prioridade="baixa", status=None):
    dados = SimpleNamespace(
        titulo=titulo,
        descricao=descricao,
        categoria=categoria,
        prioridade=prioridade,
    )
    solicitacao = database.criar_solicitacao(dados)
    if status:
        conn = database.get_connection()
        try:
            conn.execute(
                "UPDATE solicitacoes SET status = ? WHERE id = ?",
                (status, solicitacao["id"]),
            )
            conn.commit()
        finally:
            conn.close()
        solicitacao["status"] = status
    return solicitacao


def test_transicao_aberta_para_em_andamento_valida():
    # Não deve levantar exceção
    validar_transicao("Aberta", "Em andamento")


def test_transicao_em_andamento_para_concluida_valida():
    # Não deve levantar exceção
    validar_transicao("Em andamento", "Concluída")


def test_pular_etapa_aberta_para_concluida_invalida():
    with pytest.raises(TransicaoInvalidaError) as exc_info:
        validar_transicao("Aberta", "Concluída")
    assert "Em andamento" in str(exc_info.value)


def test_voltar_etapa_em_andamento_para_aberta_invalida():
    with pytest.raises(TransicaoInvalidaError) as exc_info:
        validar_transicao("Em andamento", "Aberta")
    assert "Concluída" in str(exc_info.value)


@pytest.mark.parametrize("status", ["Aberta", "Em andamento"])
def test_manter_mesmo_status_invalido(status):
    with pytest.raises(TransicaoInvalidaError) as exc_info:
        validar_transicao(status, status)
    assert "já está com o status" in str(exc_info.value)


@pytest.mark.parametrize("novo_status", ["Aberta", "Em andamento", "Concluída"])
def test_alterar_solicitacao_ja_concluida_invalida(novo_status):
    with pytest.raises(TransicaoInvalidaError) as exc_info:
        validar_transicao("Concluída", novo_status)
    assert "já está 'Concluída'" in str(exc_info.value)


def test_status_desconhecido_invalido():
    with pytest.raises(TransicaoInvalidaError):
        validar_transicao("Cancelada", "Aberta")


def test_busca_por_titulo(banco_temporario):
    adicionar_solicitacao("Criar acesso ao Figma", "Liberar conta")
    adicionar_solicitacao("Renovar domínio", "Atualizar registro")

    resultados = database.listar_solicitacoes(busca="Figma")

    assert len(resultados) == 1
    assert resultados[0]["titulo"] == "Criar acesso ao Figma"


def test_busca_por_descricao(banco_temporario):
    adicionar_solicitacao("Reembolso", "Nota fiscal já anexada")
    adicionar_solicitacao("Domínio", "Renovar assinatura")

    resultados = database.listar_solicitacoes(busca="nota fiscal")

    assert len(resultados) == 1
    assert resultados[0]["descricao"] == "Nota fiscal já anexada"


def test_busca_combinada_com_status_e_prioridade(banco_temporario):
    adicionar_solicitacao(
        "Erro no deploy", "Falha no build", prioridade="alta",
        status="Em andamento",
    )
    adicionar_solicitacao(
        "Erro no sistema", "Falha no banco", prioridade="alta",
        status="Aberta",
    )

    resultados = database.listar_solicitacoes(
        status="Em andamento",
        prioridade="alta",
        busca="deploy",
    )

    assert len(resultados) == 1
    assert resultados[0]["titulo"] == "Erro no deploy"


def test_busca_nao_interpreta_sql_injetado(banco_temporario):
    adicionar_solicitacao("Solicitação normal", "Descrição comum")

    resultados = database.listar_solicitacoes(
        busca="' OR 1=1 --"
    )

    assert resultados == []


def test_resumo_por_status(banco_temporario):
    adicionar_solicitacao("Aberta", "Primeira", status="Aberta")
    adicionar_solicitacao("Andamento", "Segunda", status="Em andamento")
    adicionar_solicitacao("Concluída", "Terceira", status="Concluída")

    resumo = database.resumo_por_status()

    assert resumo["total"] == 3
    assert resumo["por_status"] == {
        "Aberta": 1,
        "Em andamento": 1,
        "Concluída": 1,
    }