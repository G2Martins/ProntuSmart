from pydantic import Field
from enum import Enum
from src.models.base import MongoBaseModel

class DirecaoMelhora(str, Enum):
    MAIOR_MELHOR = "maior_melhor" # Ex: Força Muscular (Grau 0 a 5)
    MENOR_MELHOR = "menor_melhor" # Ex: Dor na escala EVA (10 para 0)

class DimIndicador(MongoBaseModel):
    nome: str = Field(..., description="Nome do teste/indicador funcional")
    unidade_medida: str = Field(..., description="Ex: graus, cm, pontos, kg")
    direcao_melhora: DirecaoMelhora = Field(..., description="Define como o % de progresso é calculado")