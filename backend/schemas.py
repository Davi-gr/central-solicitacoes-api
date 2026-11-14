from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SolicitacaoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(min_length=1, max_length=100)
    descricao: str = Field(min_length=1)
    categoria: str = Field(min_length=1, max_length=50)
    prioridade: Literal["baixa", "media", "alta"]


class SolicitacaoResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    categoria: str
    prioridade: str
    status: str
    criado_em: str