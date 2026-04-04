from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CidBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=10)
    descricao: str = Field(..., min_length=3, max_length=255)

class CidCreate(CidBase):
    pass

class CidUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=3, max_length=10)
    descricao: Optional[str] = Field(None, min_length=3, max_length=255)
    is_ativo: Optional[bool] = None

class CidResponse(CidBase):
    id: str = Field(alias="_id")
    is_ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)