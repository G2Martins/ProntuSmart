from pydantic import Field
from enum import Enum
from typing import Optional
from src.models.base import MongoBaseModel

class DirecaoMelhora(str, Enum):
    MAIOR_MELHOR = "maior_melhor"
    MENOR_MELHOR = "menor_melhor"

class DimIndicador(MongoBaseModel):
    nome: str = Field(..., description="Nome do teste/indicador funcional")
    descricao: Optional[str] = Field(None, description="O que este teste avalia") 
    unidade_medida: str = Field(..., description="Ex: graus, cm, pontos, kg")
    direcao_melhora: DirecaoMelhora = Field(..., description="Define como o % de progresso é calculado")
    is_ativo: bool = Field(default=True, description="Permite inativar sem excluir do histórico")