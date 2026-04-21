from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.dim_indicador import DirecaoMelhora

class IndicadorBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    unidade_medida: str = Field(..., min_length=1, max_length=50)
    direcao_melhora: DirecaoMelhora
    descricao: Optional[str] = None # Garantindo que a descrição trafegue
    sem_limitacao_valor: bool = True
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None

class IndicadorCreate(IndicadorBase):
    pass

class IndicadorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    unidade_medida: Optional[str] = Field(None, min_length=1, max_length=50)
    direcao_melhora: Optional[DirecaoMelhora] = None
    descricao: Optional[str] = None
    sem_limitacao_valor: Optional[bool] = None
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None
    is_ativo: Optional[bool] = None 

class IndicadorResponse(IndicadorBase):
    id: str = Field(alias="_id")
    is_ativo: bool 
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
