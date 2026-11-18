from contextlib import asynccontextmanager
from typing import Optional

from pathlib import Path
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException

from . import database, services
from .schemas import (
    Prioridade,
    SolicitacaoCreate,
    SolicitacaoResponse,
    Status,
    StatusUpdate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="Central de Solicitações", lifespan=lifespan)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.post("/solicitacoes", response_model=SolicitacaoResponse, status_code=201)
def criar(dados: SolicitacaoCreate):
    return database.criar_solicitacao(dados)


@app.get("/solicitacoes", response_model=list[SolicitacaoResponse])
def listar(status: Optional[Status] = None, prioridade: Optional[Prioridade] = None):
    return database.listar_solicitacoes(status, prioridade)


@app.get("/solicitacoes/{solicitacao_id}", response_model=SolicitacaoResponse)
def detalhar(solicitacao_id: int):
    solicitacao = database.buscar_solicitacao(solicitacao_id)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return solicitacao


@app.patch("/solicitacoes/{solicitacao_id}/status", response_model=SolicitacaoResponse)
def alterar_status(solicitacao_id: int, dados: StatusUpdate):
    solicitacao = database.buscar_solicitacao(solicitacao_id)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")

    try:
        services.validar_transicao(solicitacao["status"], dados.status)
    except services.TransicaoInvalidaError as erro:
        raise HTTPException(status_code=409, detail=str(erro))

    atualizada = database.atualizar_status(
        solicitacao_id, solicitacao["status"], dados.status
    )
    if atualizada is None:
        raise HTTPException(
            status_code=409,
            detail="O status desta solicitação foi alterado por outra operação. "
            "Atualize a página e tente novamente.",
        )
    return atualizada

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")