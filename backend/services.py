# Para cada status, qual é o ÚNICO próximo status permitido.
# Concluída não aparece como chave: é o fim do fluxo.
TRANSICOES = {
    "Aberta": "Em andamento",
    "Em andamento": "Concluída",
}


class TransicaoInvalidaError(Exception):
    """Levantada quando a mudança de status não respeita o fluxo."""


def validar_transicao(status_atual: str, novo_status: str) -> None:
    if status_atual not in TRANSICOES:
        raise TransicaoInvalidaError(
            f"A solicitação já está '{status_atual}' e não pode mais ser alterada."
        )

    if novo_status == status_atual:
        raise TransicaoInvalidaError(
            f"A solicitação já está com o status '{status_atual}'."
        )

    proximo_permitido = TRANSICOES[status_atual]
    if novo_status != proximo_permitido:
        raise TransicaoInvalidaError(
            f"Transição inválida: não é possível mudar de '{status_atual}' "
            f"para '{novo_status}'. O próximo status permitido é "
            f"'{proximo_permitido}'."
        )