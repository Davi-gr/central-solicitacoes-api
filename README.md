# Central de Solicitações

Aplicação web full stack para registro, consulta, filtragem e acompanhamento de solicitações internas, substituindo controles informais por um fluxo de status estruturado, validado e persistente.

Projeto desenvolvido como desafio técnico para o processo seletivo de Desenvolvimento Júnior (Full Stack — Setor de Projetos) da Loading Jr. (UFC).

## Funcionalidades Implementadas

### Requisitos obrigatórios

- **Cadastro de Solicitações (RF01):** registro com título (máx. 100 caracteres), descrição (máx. 2000), categoria (máx. 50) e prioridade (`baixa`, `media` ou `alta`), iniciando sempre no status `Aberta`.
- **Consulta e Detalhamento (RF02):** listagem ordenada das mais recentes para as mais antigas e visualização completa dos dados em modal nativo (`<dialog>`).
- **Filtros Combinados (RF03):** filtragem da listagem por status e/ou prioridade, via query parameters na API.
- **Controle de Fluxo / Regra de Negócio (RF04):** máquina de estados que permite apenas o avanço sequencial `Aberta → Em andamento → Concluída`, bloqueando saltos de etapa, retrocessos e alterações após a conclusão.
- **Persistência em Banco de Dados (RF05):** armazenamento local em SQLite (`backend/central.db`), criado automaticamente na inicialização e mantido após reinicializações.
- **Integração e Validação (RF06):** validação de entrada e de transição no back-end, com retorno claro de erros HTTP (`422` dados inválidos, `404` recurso inexistente, `409` conflito de estado), traduzidos e exibidos na interface.

### Funcionalidades adicionais

- **Cards de resumo:** contadores de total e por status no topo da tela, calculados no banco por um endpoint com `GROUP BY`. Refletem sempre o banco inteiro, independentemente dos filtros ativos, e ao serem clicados aplicam o filtro de status correspondente.
- **Busca textual:** busca por título e descrição, combinável com os filtros de status e prioridade, com `LIKE` parametrizado, escape dos curingas `%` e `_` e *debounce* de 300 ms no front-end.
- **Dados de demonstração:** script `seed.py` que popula o banco com solicitações realistas, em diferentes status e prioridades.
- **Testes automatizados:** suíte com `pytest` cobrindo as transições válidas e inválidas da regra de negócio.

## Tecnologias e Dependências

- **Linguagem:** Python 3.12+
- **Back-end / API:** FastAPI + Uvicorn
- **Validação de dados:** Pydantic
- **Banco de dados:** SQLite3 (módulo nativo do Python, sem ORM)
- **Front-end:** HTML5, CSS3 e JavaScript puro (Fetch API e `<dialog>`), servido estaticamente pelo próprio FastAPI via `StaticFiles`
- **Testes:** Pytest

## Arquitetura e Decisões Técnicas

```
central-solicitacoes-api/
├── backend/
│   ├── __init__.py
│   ├── main.py          # Rotas HTTP, tratamento de exceções e montagem do front-end
│   ├── schemas.py       # Modelos Pydantic de entrada/saída e tipos literais
│   ├── services.py      # Máquina de estados e regra de negócio (isolada de HTTP/SQL)
│   └── database.py      # Conexão SQLite e queries SQL parametrizadas
├── frontend/
│   ├── index.html       # Estrutura semântica da interface, cards de resumo e modal
│   ├── app.js           # Consumo da API, controle de concorrência e renderização
│   └── style.css        # Estilização e badges visuais de status e prioridade
├── tests/
│   └── test_services.py # Testes unitários da regra de transição de status
├── seed.py              # Dados de demonstração
├── .gitignore
├── requirements.txt
└── README.md
```

- **Separação em camadas:** `services.py` não importa FastAPI nem `sqlite3`, o que permite testar a regra de negócio de forma pura e rápida. `database.py` não conhece códigos HTTP: devolve `None` quando não encontra o registro, e a decisão do `404` fica na camada de rotas.
- **Segurança em camadas:**
  - **Contra SQL Injection:** todas as consultas usam placeholders (`?`) e listas fechadas de valores (`Literal`). No SQL dinâmico dos filtros e da busca, apenas trechos fixos escritos no código são concatenados, e os valores do usuário vão sempre como parâmetros.
  - **Contra XSS:** no front-end, os dados retornados pela API são inseridos no DOM exclusivamente via `textContent` e `createElement`, nunca via `innerHTML`.
  - **Validação no servidor:** o formulário usa `novalidate` para delegar a validação à API e exibir suas mensagens reais, garantindo que chamadas diretas à API respeitem as mesmas regras.
- **Integridade de estado e concorrência:** a atualização de status executa `UPDATE solicitacoes SET status = ? WHERE id = ? AND status = ?`. Se duas requisições tentarem avançar o mesmo registro simultaneamente, apenas a primeira obtém `rowcount == 1`; a segunda recebe `409 Conflict` e o front-end recarrega o estado real do servidor.
- **Concorrência no front-end:** um contador de requisições descarta respostas antigas da listagem (por exemplo, ao trocar filtros rapidamente), e o *debounce* da busca evita uma requisição por tecla digitada.
- **Resumo calculado no banco:** os cards usam um endpoint próprio com `GROUP BY`, e não a lista exibida, pois a lista já chega filtrada e os contadores ficariam incorretos com um filtro ativo.
- **Busca com `LIKE` seguro:** o termo é entregue como parâmetro, e os caracteres `%` e `_` são escapados com `ESCAPE`, para serem tratados como texto comum e não como curingas.
- **Origem única:** servir o front-end estático pelo próprio FastAPI evita problemas de CORS e permite subir toda a aplicação com um único comando.

## Instalação e Execução Local

### 1. Clonar o repositório

```bash
git clone https://github.com/Davi-gr/central-solicitacoes-api.git
cd central-solicitacoes-api
```

### 2. Criar e ativar o ambiente virtual

No Windows (Git Bash):

```bash
python -m venv venv
source venv/Scripts/activate
```

(Se `python` não for reconhecido no Windows, use `py -m venv venv`.)

No Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
venv/Scripts/python -m pip install -r requirements.txt
```

(No Linux/macOS, use `python -m pip install -r requirements.txt`.)

### 4. Dados de demonstração (opcional)

Para popular o banco com solicitações de exemplo:

```bash
venv/Scripts/python seed.py
```

Se o banco já tiver dados, o script não altera nada. Para apagar tudo e recriar os dados de exemplo:

```bash
venv/Scripts/python seed.py --limpar
```

### 5. Iniciar a aplicação

Na raiz do projeto, execute:

```bash
venv/Scripts/python -m uvicorn backend.main:app --reload
```

(No Linux/macOS, use `python -m uvicorn backend.main:app --reload`.)

### 6. Acessar no navegador

- **Interface Web:** http://127.0.0.1:8000
- **Documentação interativa da API (Swagger UI):** http://127.0.0.1:8000/docs

## Executando os Testes Automatizados

Para rodar a suíte de testes unitários da regra de negócio (`services.py`), execute na raiz do projeto:

```bash
venv/Scripts/python -m pytest -v
```

## Rotas da API

| Método | Rota | Descrição | Códigos HTTP |
|---|---|---|---|
| `POST` | `/solicitacoes` | Cria uma nova solicitação com status inicial `Aberta` | 201, 422 |
| `GET` | `/solicitacoes` | Lista solicitações. Parâmetros opcionais: `status`, `prioridade` e `busca` (título ou descrição, até 100 caracteres) | 200, 422 |
| `GET` | `/solicitacoes/resumo` | Total de solicitações e contagem por status | 200 |
| `GET` | `/solicitacoes/{id}` | Consulta os detalhes de uma solicitação | 200, 404, 422 |
| `PATCH` | `/solicitacoes/{id}/status` | Avança o status conforme o fluxo permitido | 200, 404, 409, 422 |

Exemplo: `GET /solicitacoes?status=Aberta&prioridade=alta&busca=deploy`

A rota `/solicitacoes/resumo` é declarada antes de `/solicitacoes/{id}`: o FastAPI avalia as rotas na ordem de declaração, e a rota com variável capturaria `resumo` como se fosse um id.

## Como Evoluir a Solução

A arquitetura atual permite expandir o sistema sem reescrever o núcleo:

- **Novos fluxos de status:** bastaria ajustar o dicionário `TRANSICOES` em `backend/services.py` (ou evoluir para uma lista de destinos permitidos por estado, caso surjam estados como `Cancelada`).
- **Histórico de auditoria:** criação de uma tabela `historico_status` gravada dentro da mesma transação de `atualizar_status` em `backend/database.py`.
- **Autenticação e permissões:** inclusão de dependências (`Depends`) no FastAPI para validar tokens JWT nas rotas de escrita (`POST` e `PATCH`).
- **Paginação:** `LIMIT` e `OFFSET` na listagem, com o total devolvido para a interface.
- **Busca mais robusta:** uso do FTS5 do SQLite, ou normalização de acentos, para uma busca que ignore acentuação.

## Limitações Conhecidas

Por se tratar de um escopo enxuto, focado na consistência do fluxo principal e na execução local:

- Não possui autenticação nem controle de perfis de usuário.
- Não possui paginação nem limite de taxa (*rate limiting*) nas rotas.
- A busca usa `LIKE` do SQLite, que ignora maiúsculas e minúsculas apenas em letras sem acento (por exemplo, `acao` não encontra `Ação`).
- Utiliza IDs inteiros sequenciais e banco SQLite em arquivo local (`backend/central.db`), adequado para uso local e demonstração, mas que exigiria migração para PostgreSQL ou MySQL em um ambiente com múltiplas instâncias.
- O `seed.py` grava no mesmo arquivo de banco da aplicação, e o `--limpar` apaga todas as solicitações existentes.

## Declaração de Uso de Inteligência Artificial

Em conformidade com as diretrizes do processo seletivo, ferramentas de Inteligência Artificial (Claude, da Anthropic, e Gemini, do Google) foram utilizadas como apoio durante o desenvolvimento, em atividades como:

- Esclarecimento de conceitos e boas práticas do ecossistema FastAPI, Pydantic, SQLite e HTTP;
- Proposta de estrutura do projeto e de trechos de código (back-end, front-end, script de seed e casos de teste), que foram adaptados pelo autor;
- Revisão da separação entre camadas, do tratamento de erros HTTP (404, 409, 422), da prevenção de condições de corrida, de SQL Injection e de XSS;
- Apoio na depuração de erros e na revisão da documentação.

Todo o código foi executado e testado manualmente (interface web e Swagger UI) e por testes automatizados, e foi revisado linha a linha pelo autor, que consegue explicar e justificar as decisões adotadas.
