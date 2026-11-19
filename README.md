# Central de Solicitações

Aplicação web full stack para registro, consulta, filtragem e acompanhamento de solicitações internas, substituindo controles informais por um fluxo de status estruturado, validado e persistente.

Projeto desenvolvido como desafio técnico para o processo seletivo de Desenvolvimento Júnior (Full Stack — Setor de Projetos) da **Loading Jr. (UFC)**.

---

## Funcionalidades Implementadas

- **Cadastro de Solicitações (RF01):** Registro com título (máx. 100 caracteres), descrição (máx. 2000 caracteres), categoria (máx. 50 caracteres) e prioridade (`baixa`, `media` ou `alta`), iniciando sempre no status `Aberta`.
- **Consulta e Detalhamento (RF02):** Listagem ordenada das solicitações mais recentes para as mais antigas e visualização completa dos dados em modal nativo (`<dialog>`).
- **Filtros Combinados (RF03):** Filtragem dinâmica da listagem por `status` e/ou `prioridade` via query parameters na API.
- **Controle de Fluxo / Regra de Negócio (RF04):** Máquina de estados rigorosa que permite apenas o avanço sequencial `Aberta` → `Em andamento` → `Concluída`, bloqueando saltos de etapa, retrocessos ou alterações após a conclusão.
- **Persistência em Banco de Dados (RF05):** Armazenamento local em SQLite (`backend/central.db`), criado automaticamente na inicialização da aplicação e mantido após reinicializações.
- **Integração e Validação (RF06):** Validação rigorosa de entrada e transição no back-end com retorno claro de erros HTTP (`422` para dados inválidos, `404` para recurso inexistente e `409` para conflito de estado) tratados e exibidos na interface.
- **Testes Automatizados (Opcional):** Suíte de testes unitários com `pytest` cobrindo todas as transições válidas e inválidas da regra de negócio.

---

## Tecnologias e Dependências

- **Linguagem:** Python 3.12+
- **Back-end / API:** FastAPI + Uvicorn
- **Validação de Dados:** Pydantic
- **Banco de Dados:** SQLite3 (módulo nativo do Python, sem ORM)
- **Front-end:** HTML5, CSS3 e JavaScript puro (Vanilla JS com Fetch API e `<dialog>`), servido estaticamente pelo próprio FastAPI via `StaticFiles`
- **Testes:** Pytest

---

## Arquitetura e Decisões Técnicas

```text
central-solicitacoes/
├── backend/
│   ├── __init__.py
│   ├── main.py          # Rotas HTTP, tratamento de exceções e montagem do front-end
│   ├── schemas.py       # Modelos Pydantic de entrada/saída e tipos literais
│   ├── services.py      # Máquina de estados e regra de negócio (isolada de HTTP/SQL)
│   └── database.py      # Conexão SQLite e queries SQL parametrizadas
├── frontend/
│   ├── index.html       # Estrutura semântica da interface e modal de detalhes
│   ├── app.js           # Consumo da API, controle de concorrência e renderização
│   └── style.css        # Estilização e badges visuais de status e prioridade
├── tests/
│   └── test_services.py # Testes unitários da regra de transição de status
├── .gitignore
├── requirements.txt
└── README.md
```

- **Separação em camadas:** `services.py` não importa FastAPI nem `sqlite3`, permitindo testar a regra de negócio de forma pura e rápida. `database.py` não conhece códigos HTTP (devolve `None` quando não encontra registro, deixando a decisão do `404` para a camada de rotas).
- **Segurança em camadas:**
  - **Contra SQL Injection:** Todas as consultas utilizam placeholders (`?`) e listas fechadas de valores (`Literal`), sem concatenação de entradas do usuário.
  - **Contra XSS:** No front-end, os dados retornados pela API são inseridos no DOM exclusivamente via `textContent` e `createElement`, nunca via `innerHTML`.
  - **Validação no servidor:** O front-end utiliza `novalidate` para delegar a validação à API e exibir suas mensagens reais, garantindo que chamadas diretas à API respeitem as mesmas regras.
- **Integridade de estado e concorrência:** A atualização de status executa `UPDATE solicitacoes SET status = ? WHERE id = ? AND status = ?`. Se duas requisições tentarem avançar o mesmo registro simultaneamente, apenas a primeira obtém `rowcount == 1`; a segunda recebe `409 Conflict` e o front-end recarrega automaticamente o estado real do servidor.
- **Origem única:** Servir o front-end estático pelo próprio FastAPI evita problemas de CORS e permite subir toda a aplicação com um único comando.

---

## Instalação e Execução Local

### 1. Clonar o repositório
```bash
git clone https://github.com/Davi-gr/central-solicitacoes-api.git
cd central-solicitacoes
```

### 2. Criar e ativar o ambiente virtual

**No Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências
```bash
venv/Scripts/python -m pip install -r requirements.txt
```
*(No Linux/macOS, utilize `python -m pip install -r requirements.txt`).*

## 4. Dados de demonstração

Para popular o banco com solicitações de exemplo:

    venv/Scripts/python seed.py

Se o banco já tiver dados, o script não altera nada. Para apagar tudo e recriar: `seed.py --limpar`.

### 5. Iniciar a aplicação
Na raiz do projeto (`central-solicitacoes/`), execute:

```bash
venv/Scripts/python -m uvicorn backend.main:app --reload
```
*(No Linux/macOS, utilize `uvicorn backend.main:app --reload`).*

### 6. Acessar no navegador
- **Interface Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Interativa da API (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Executando os Testes Automatizados

Para rodar a suíte de testes unitários da regra de negócio (`services.py`), execute na raiz do projeto:

```bash
venv/Scripts/python -m pytest -v
```

---

## Rotas da API

| Método | Rota | Descrição | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `POST` | `/solicitacoes` | Cria uma nova solicitação com status inicial `Aberta` | `201`, `422` |
| `GET` | `/solicitacoes` | Lista solicitações (filtros opcionais: `?status=&prioridade=`) | `200`, `422` |
| `GET` | `/solicitacoes/{id}` | Consulta os detalhes de uma solicitação específica | `200`, `404`, `422` |
| `PATCH` | `/solicitacoes/{id}/status` | Avança o status conforme o fluxo permitido | `200`, `404`, `409`, `422` |

---

## Como Evoluir a Solução

A arquitetura atual permite expandir o sistema sem reescrever o núcleo:
- **Novos fluxos de status:** Bastaria ajustar o dicionário `TRANSICOES` em `backend/services.py` (ou evoluir para uma lista de destinos permitidos por estado, caso surjam estados como `Cancelada`).
- **Histórico de auditoria:** Criação de uma tabela `historico_status` gravada dentro da mesma transação de `atualizar_status` em `backend/database.py`.
- **Autenticação e permissões:** Inclusão de dependências (`Depends`) no FastAPI para validar tokens JWT nas rotas de escrita (`POST` e `PATCH`).

---

## Limitações Conhecidas

Por se tratar de um escopo enxuto focado na consistência do fluxo principal e execução local:
- Não possui autenticação ou controle de perfis de usuário.
- Não possui paginação nem limite de taxa (*rate limiting*) nas rotas.
- Utiliza IDs inteiros sequenciais e banco SQLite em arquivo local (`backend/central.db`), adequado para uso local/demonstração, mas que exigiria migração para PostgreSQL/MySQL em ambiente multi-instância.

---

## Declaração de Uso de Inteligência Artificial

Em conformidade com as diretrizes do processo seletivo, ferramentas de Inteligência Artificial (Gemini) foram utilizadas como apoio durante o desenvolvimento para:
- Esclarecimento de conceitos e boas práticas do ecossistema FastAPI e Pydantic;
- Revisão arquitetural da separação entre camadas (`main`, `schemas`, `services`, `database`), tratamento de erros HTTP (`404`, `409`, `422`) e prevenção de condições de corrida e XSS;
- Apoio na estruturação dos casos de teste unitários com `pytest` e revisão da documentação.

Todo o código foi implementado incrementalmente, testado manualmente via interface web e Swagger UI, validado por testes automatizados e revisado linha a linha pelo autor.