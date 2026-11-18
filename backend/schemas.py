from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Prioridade = Literal["baixa", "media", "alta"]
Status = Literal["Aberta", "Em andamento", "Concluída"]


class SolicitacaoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(min_length=1, max_length=100)
    descricao: str = Field(min_length=1, max_length=2000)
    categoria: str = Field(min_length=1, max_length=50)
    prioridade: Prioridade


class StatusUpdate(BaseModel):
    status: Status


class SolicitacaoResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    categoria: str
    prioridade: str
    status: str
    criado_em: str