const API = "/solicitacoes";

const form = document.getElementById("form-solicitacao");
const areaMensagem = document.getElementById("mensagem");
const corpoTabela = document.getElementById("lista");

const NOMES_CAMPOS = {
  titulo: "Título",
  descricao: "Descrição",
  categoria: "Categoria",
  prioridade: "Prioridade",
  status: "Status",
};

const ROTULOS_PRIORIDADE = { baixa: "Baixa", media: "Média", alta: "Alta" };


function mostrarMensagem(mensagens, tipo) {
  areaMensagem.replaceChildren();
  areaMensagem.className = tipo;
  for (const texto of mensagens) {
    const paragrafo = document.createElement("p");
    paragrafo.textContent = texto;
    areaMensagem.appendChild(paragrafo);
  }
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


function renderizarTabela(lista) {
  corpoTabela.replaceChildren();

  if (lista.length === 0) {
    const linha = document.createElement("tr");
    const celula = document.createElement("td");
    celula.colSpan = 6;
    celula.textContent = "Nenhuma solicitação cadastrada.";
    linha.appendChild(celula);
    corpoTabela.appendChild(linha);
    return;
  }

  for (const item of lista) {
    const linha = document.createElement("tr");
    const valores = [
      item.id,
      item.titulo,
      item.categoria,
      ROTULOS_PRIORIDADE[item.prioridade] || item.prioridade,
      item.status,
      formatarData(item.criado_em),
    ];
    for (const valor of valores) {
      const celula = document.createElement("td");
      celula.textContent = valor;
      linha.appendChild(celula);
    }
    corpoTabela.appendChild(linha);
  }
}


async function carregarSolicitacoes() {
  try {
    const resposta = await fetch(API);
    const corpo = await lerJson(resposta);
    if (!resposta.ok) {
      mostrarMensagem(extrairErros(corpo), "erro");
      return;
    }
    renderizarTabela(corpo);
  } catch {
    mostrarMensagem(["Não foi possível conectar ao servidor."], "erro");
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
      mostrarMensagem(extrairErros(corpo), "erro");
      return;
    }

    form.reset();
    mostrarMensagem(["Solicitação cadastrada com sucesso."], "sucesso");
    await carregarSolicitacoes();
  } catch {
    mostrarMensagem(["Não foi possível conectar ao servidor."], "erro");
  }
}


form.addEventListener("submit", enviarFormulario);
carregarSolicitacoes();