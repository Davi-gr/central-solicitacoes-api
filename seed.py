import sys
from datetime import datetime, timedelta

from backend import database, services
from backend.schemas import SolicitacaoCreate

# (título, descrição, categoria, prioridade, status final, horas atrás)
# Da mais antiga para a mais recente, para os ids seguirem a cronologia.
DADOS = [
    (
        "Atualizar certificados da última capacitação",
        "Os certificados ainda trazem o nome do evento antigo. Gerar de novo com o template atualizado e enviar aos participantes.",
        "Gestão de Pessoas", "baixa", "Concluída", 168,
    ),
    (
        "Renovar domínio do site institucional",
        "O domínio vence no fim do mês. Renovar por 12 meses e atualizar o responsável no registro.",
        "Tecnologia", "alta", "Concluída", 120,
    ),
    (
        "Solicitar reembolso de material do evento",
        "Reembolsar a compra de materiais de papelaria do último evento. Nota fiscal já anexada na pasta compartilhada.",
        "Financeiro", "media", "Em andamento", 72,
    ),
    (
        "Revisar identidade visual dos posts do Instagram",
        "Padronizar cores e fontes dos posts para seguir o manual de marca atualizado.",
        "Marketing", "baixa", "Aberta", 48,
    ),
    (
        "Erro no deploy do site institucional",
        "O deploy de ontem falhou e a página de projetos está fora do ar. Verificar o log do build e a versão das dependências.",
        "Tecnologia", "alta", "Em andamento", 26,
    ),
    (
        "Reparo no ar-condicionado da sala da EJ",
        "O aparelho está pingando e não refrigera. Acionar a manutenção do prédio antes da próxima reunião geral.",
        "Infraestrutura", "alta", "Aberta", 8,
    ),
    (
        "Criar acesso ao Figma para novos trainees",
        "Liberar contas no time de design para os trainees que entraram nesta semana.",
        "Acessos", "media", "Aberta", 2,
    ),
]


def contar():
    conn = database.get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM solicitacoes").fetchone()[0]
    finally:
        conn.close()


def limpar():
    conn = database.get_connection()
    try:
        conn.execute("DELETE FROM solicitacoes")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'solicitacoes'")
        conn.commit()
    finally:
        conn.close()


def definir_data_criacao(solicitacao_id, horas_atras):
    criado_em = (datetime.now() - timedelta(hours=horas_atras)).isoformat(
        timespec="seconds"
    )
    conn = database.get_connection()
    try:
        conn.execute(
            "UPDATE solicitacoes SET criado_em = ? WHERE id = ?",
            (criado_em, solicitacao_id),
        )
        conn.commit()
    finally:
        conn.close()


def avancar_ate(solicitacao_id, status_final):
    atual = "Aberta"
    while atual != status_final:
        proximo = services.TRANSICOES[atual]
        services.validar_transicao(atual, proximo)
        database.atualizar_status(solicitacao_id, atual, proximo)
        atual = proximo


def main():
    database.init_db()
    existentes = contar()

    if "--limpar" in sys.argv:
        limpar()
    elif existentes > 0:
        print(f"O banco já tem {existentes} solicitações. Nada foi alterado.")
        print("Use --limpar para apagar tudo e recriar os dados de demonstração.")
        return

    for titulo, descricao, categoria, prioridade, status, horas in DADOS:
        dados = SolicitacaoCreate(
            titulo=titulo,
            descricao=descricao,
            categoria=categoria,
            prioridade=prioridade,
        )
        criada = database.criar_solicitacao(dados)
        avancar_ate(criada["id"], status)
        definir_data_criacao(criada["id"], horas)

    print(f"{len(DADOS)} solicitações de demonstração criadas.")


if __name__ == "__main__":
    main()