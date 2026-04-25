from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.fato_teste import TipoTeste


class TesteCreate(BaseModel):
    prontuario_id:    str
    tipo:             TipoTeste
    dados:            dict = Field(default_factory=dict)
    pontuacao_total:  Optional[float] = None
    pontuacao_maxima: Optional[float] = None
    interpretacao:    Optional[str]   = None
    observacoes:      Optional[str]   = None


class TesteUpdate(BaseModel):
    dados:            Optional[dict]  = None
    pontuacao_total:  Optional[float] = None
    pontuacao_maxima: Optional[float] = None
    interpretacao:    Optional[str]   = None
    observacoes:      Optional[str]   = None


class TesteResponse(BaseModel):
    id:               str = Field(alias="_id")
    prontuario_id:    str
    paciente_id:      str
    aplicador_id:     str
    nome_aplicador:   Optional[str] = None
    tipo:             TipoTeste
    dados:            dict
    pontuacao_total:  Optional[float] = None
    pontuacao_maxima: Optional[float] = None
    interpretacao:    Optional[str]   = None
    observacoes:      Optional[str]   = None
    data_aplicacao:   datetime
    criado_em:        datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
