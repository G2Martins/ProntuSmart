from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class AreaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = None
    icone: str
    cor: str

class AreaCreate(AreaBase):
    pass

class AreaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = None
    icone: Optional[str] = None
    cor: Optional[str] = None
    is_ativo: Optional[bool] = None

class AreaResponse(AreaBase):
    id: str = Field(alias="_id")
    is_ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)