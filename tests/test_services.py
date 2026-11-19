import pytest

from backend.services import TransicaoInvalidaError, validar_transicao


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