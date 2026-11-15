from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException

from . import database
from .schemas import Prioridade, SolicitacaoCreate, SolicitacaoResponse, Status

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()  # cria a tabela ao iniciar o servidor
    yield


app = FastAPI(title="Central de Solicitações", lifespan=lifespan)


@app.post("/solicitacoes", response_model=SolicitacaoResponse, status_code=201)
def criar(dados: SolicitacaoCreate):
    return database.criar_solicitacao(dados)


@app.get("/solicitacoes", response_model=list[SolicitacaoResponse])
def listar(status: Optional[Status] = None, prioridade: Optional[Prioridade] = None):
    return database.listar_solicitacoes(status, prioridade)


@app.get("/solicitacoes/{id}", response_model=SolicitacaoResponse)
def detalhar(id: int):
    solicitacao = database.buscar_solicitacao(id)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return solicitacao