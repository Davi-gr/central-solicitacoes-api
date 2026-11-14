from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import database
from .schemas import SolicitacaoCreate, SolicitacaoResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()  # cria a tabela ao iniciar o servidor
    yield


app = FastAPI(title="Central de Solicitações", lifespan=lifespan)


@app.post("/solicitacoes", response_model=SolicitacaoResponse, status_code=201)
def criar(dados: SolicitacaoCreate):
    return database.criar_solicitacao(dados)