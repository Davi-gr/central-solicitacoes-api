const API = "/solicitacoes";

const PROXIMO_STATUS = {
  "Aberta": "Em andamento",
  "Em andamento": "Concluída",
};

const NOMES_CAMPOS = {
  titulo: "Título",
  descricao: "Descrição",
  categoria: "Categoria",
  prioridade: "Prioridade",
  status: "Status",
};

const ROTULOS_PRIORIDADE = { baixa: "Baixa", media: "Média", alta: "Alta" };

const CLASSES_PRIORIDADE = {
  baixa: "prioridade-baixa",
  media: "prioridade-media",
  alta: "prioridade-alta",
};

const CLASSES_STATUS = {
  "Aberta": "status-aberta",
  "Em andamento": "status-andamento",
  "Concluída": "status-concluida",
};

const form = document.getElementById("form-solicitacao");
const areaMensagem = document.getElementById("mensagem");
const corpoTabela = document.getElementById("lista");
const filtroStatus = document.getElementById("filtro-status");
const filtroPrioridade = document.getElementById("filtro-prioridade");
const filtroBusca = document.getElementById("filtro-busca");
const botaoLimpar = document.getElementById("limpar-filtros");

const dialogo = document.getElementById("dialogo");
const areaMensagemDetalhe = document.getElementById("mensagem-detalhe");
const botaoAvancar = document.getElementById("botao-avancar");
const botaoFechar = document.getElementById("botao-fechar");

let solicitacaoAberta = null;
let contadorLista = 0;
let temporizadorBusca = null;


function mostrarMensagem(area, mensagens, tipo) {
  area.replaceChildren();
  area.className = tipo;
  for (const texto of mensagens) {
    const paragrafo = document.createElement("p");
    paragrafo.textContent = texto;
    area.appendChild(paragrafo);
  }
}


function limparMensagem(area) {
  area.replaceChildren();
  area.className = "";
}


async function lerJson(resposta) {
  try {
    return await resposta.json();
  } catch {
    return null;
  }
}


function formatarErroCampo(erro) {
  const campo = erro.loc[erro.loc.length - 1];
  const nome = NOMES_CAMPOS[campo] || campo;

  switch (erro.type) {
    case "string_too_short":
    case "missing":
      return `${nome}: campo obrigatório, não pode ficar vazio.`;
    case "string_too_long":
      return `${nome}: máximo de ${erro.ctx?.max_length} caracteres.`;
    case "literal_error":
      return `${nome}: valor inválido.`;
    default:
      return `${nome}: ${erro.msg}`;
  }
}


function extrairErros(corpo) {
  if (!corpo || corpo.detail === undefined) {
    return ["Erro inesperado no servidor. Tente novamente."];
  }
  if (typeof corpo.detail === "string") {
    return [corpo.detail];
  }
  if (Array.isArray(corpo.detail)) {
    return corpo.detail.map(formatarErroCampo);
  }
  return ["Erro inesperado."];
}


function formatarData(iso) {
  return new Date(iso).toLocaleString("pt-BR");
}


function criarBadge(texto, classe) {
  const badge = document.createElement("span");
  badge.className = `badge ${classe || "badge-neutro"}`;
  badge.textContent = texto;
  return badge;
}


function criarCelula(conteudo) {
  const celula = document.createElement("td");
  if (conteudo instanceof Node) {
    celula.appendChild(conteudo);
  } else {
    celula.textContent = conteudo;
  }
  return celula;
}


function renderizarTabela(lista) {
  corpoTabela.replaceChildren();

  if (lista.length === 0) {
    const filtrando =
      filtroStatus.value || filtroPrioridade.value || filtroBusca.value.trim();
    const linha = document.createElement("tr");
    const celula = document.createElement("td");
    celula.colSpan = 7;
    celula.textContent = filtrando
      ? "Nenhuma solicitação encontrada com esses filtros."
      : "Nenhuma solicitação cadastrada.";
    linha.appendChild(celula);
    corpoTabela.appendChild(linha);
    return;
  }

  for (const item of lista) {
    const botaoDetalhes = document.createElement("button");
    botaoDetalhes.type = "button";
    botaoDetalhes.textContent = "Detalhes";
    botaoDetalhes.addEventListener("click", () => abrirDetalhe(item.id));

    const linha = document.createElement("tr");
    linha.appendChild(criarCelula(item.id));
    linha.appendChild(criarCelula(item.titulo));
    linha.appendChild(criarCelula(item.categoria));
    linha.appendChild(
      criarCelula(
        criarBadge(
          ROTULOS_PRIORIDADE[item.prioridade] || item.prioridade,
          CLASSES_PRIORIDADE[item.prioridade]
        )
      )
    );
    linha.appendChild(
      criarCelula(criarBadge(item.status, CLASSES_STATUS[item.status]))
    );
    linha.appendChild(criarCelula(formatarData(item.criado_em)));
    linha.appendChild(criarCelula(botaoDetalhes));
    corpoTabela.appendChild(linha);
  }
}


async function carregarSolicitacoes() {
  const numero = ++contadorLista;

  const params = new URLSearchParams();
  if (filtroStatus.value) params.set("status", filtroStatus.value);
  if (filtroPrioridade.value) params.set("prioridade", filtroPrioridade.value);
  if (filtroBusca.value.trim()) params.set("busca", filtroBusca.value.trim());
  const consulta = params.toString();
  const url = consulta ? `${API}?${consulta}` : API;

  try {
    const resposta = await fetch(url);
    const corpo = await lerJson(resposta);

    if (numero !== contadorLista) return;

    if (!resposta.ok) {
      mostrarMensagem(areaMensagem, extrairErros(corpo), "erro");
      return;
    }
    renderizarTabela(corpo);
  } catch {
    if (numero !== contadorLista) return;
    mostrarMensagem(areaMensagem, ["Não foi possível conectar ao servidor."], "erro");
  }
}

async function carregarResumo() {
  try {
    const resposta = await fetch(`${API}/resumo`);
    const corpo = await lerJson(resposta);
    if (!resposta.ok) return;

    const porStatus = corpo.por_status;
    document.getElementById("resumo-total").textContent = corpo.total;
    document.getElementById("resumo-aberta").textContent = porStatus["Aberta"] ?? 0;
    document.getElementById("resumo-andamento").textContent = porStatus["Em andamento"] ?? 0;
    document.getElementById("resumo-concluida").textContent = porStatus["Concluída"] ?? 0;
  } catch {
    // o resumo é secundário: se falhar, a lista já mostra o erro de conexão
  }
}

function limparFiltros() {
  filtroStatus.value = "";
  filtroPrioridade.value = "";
  filtroBusca.value = "";
  carregarSolicitacoes();
}


async function buscarSolicitacao(id) {
  const resposta = await fetch(`${API}/${id}`);
  const corpo = await lerJson(resposta);
  return { ok: resposta.ok, corpo };
}


function preencherDetalhe(s) {
  solicitacaoAberta = s;

  document.getElementById("d-titulo").textContent = s.titulo;
  document.getElementById("d-id").textContent = s.id;
  document.getElementById("d-descricao").textContent = s.descricao;
  document.getElementById("d-categoria").textContent = s.categoria;
  document.getElementById("d-criado").textContent = formatarData(s.criado_em);

  document.getElementById("d-prioridade").replaceChildren(
    criarBadge(
      ROTULOS_PRIORIDADE[s.prioridade] || s.prioridade,
      CLASSES_PRIORIDADE[s.prioridade]
    )
  );
  document.getElementById("d-status").replaceChildren(
    criarBadge(s.status, CLASSES_STATUS[s.status])
  );

  const proximo = PROXIMO_STATUS[s.status];
  botaoAvancar.hidden = !proximo;
  if (proximo) {
    botaoAvancar.textContent = `Avançar para "${proximo}"`;
  }
}


async function abrirDetalhe(id) {
  limparMensagem(areaMensagemDetalhe);
  try {
    const resultado = await buscarSolicitacao(id);
    if (!resultado.ok) {
      mostrarMensagem(areaMensagem, extrairErros(resultado.corpo), "erro");
      return;
    }
    preencherDetalhe(resultado.corpo);
    if (!dialogo.open) dialogo.showModal();
  } catch {
    mostrarMensagem(areaMensagem, ["Não foi possível conectar ao servidor."], "erro");
  }
}


async function avancarStatus() {
  if (!solicitacaoAberta) return;

  const id = solicitacaoAberta.id;
  const proximo = PROXIMO_STATUS[solicitacaoAberta.status];
  if (!proximo) return;

  botaoAvancar.disabled = true;
  limparMensagem(areaMensagemDetalhe);

  try {
    const resposta = await fetch(`${API}/${id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: proximo }),
    });
    const corpo = await lerJson(resposta);

    if (!resposta.ok) {
      mostrarMensagem(areaMensagemDetalhe, extrairErros(corpo), "erro");
      const atual = await buscarSolicitacao(id);
      if (atual.ok) preencherDetalhe(atual.corpo);
      await carregarSolicitacoes();
      return;
    }

    preencherDetalhe(corpo);
    mostrarMensagem(
      areaMensagemDetalhe,
      [`Status alterado para "${corpo.status}".`],
      "sucesso"
    );
    await carregarSolicitacoes();
    await carregarResumo();
  } catch {
    mostrarMensagem(
      areaMensagemDetalhe,
      ["Não foi possível conectar ao servidor."],
      "erro"
    );
  } finally {
    botaoAvancar.disabled = false;
  }
}


async function enviarFormulario(evento) {
  evento.preventDefault();

  const dados = {
    titulo: form.elements.titulo.value,
    descricao: form.elements.descricao.value,
    categoria: form.elements.categoria.value,
    prioridade: form.elements.prioridade.value,
  };

  try {
    const resposta = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    const corpo = await lerJson(resposta);

    if (!resposta.ok) {
      mostrarMensagem(areaMensagem, extrairErros(corpo), "erro");
      return;
    }

    form.reset();
    mostrarMensagem(areaMensagem, ["Solicitação cadastrada com sucesso."], "sucesso");
    await carregarSolicitacoes();
    await carregarResumo();
  } catch {
    mostrarMensagem(areaMensagem, ["Não foi possível conectar ao servidor."], "erro");
  }
}


form.addEventListener("submit", enviarFormulario);
filtroStatus.addEventListener("change", carregarSolicitacoes);
filtroPrioridade.addEventListener("change", carregarSolicitacoes);
filtroBusca.addEventListener("input", () => {
  clearTimeout(temporizadorBusca);
  temporizadorBusca = setTimeout(carregarSolicitacoes, 300);
});
botaoLimpar.addEventListener("click", limparFiltros);
botaoAvancar.addEventListener("click", avancarStatus);
botaoFechar.addEventListener("click", () => dialogo.close());
dialogo.addEventListener("click", (evento) => {
  if (evento.target === dialogo) dialogo.close();
});
for (const card of document.querySelectorAll(".card[data-status]")) {
  card.addEventListener("click", () => {
    filtroStatus.value = card.dataset.status;
    carregarSolicitacoes();
  });
}

carregarSolicitacoes();
carregarResumo();