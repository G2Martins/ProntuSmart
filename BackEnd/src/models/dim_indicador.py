from pydantic import Field
from enum import Enum
from typing import List, Optional
from src.models.base import MongoBaseModel

class DirecaoMelhora(str, Enum):
    MAIOR_MELHOR = "maior_melhor"
    MENOR_MELHOR = "menor_melhor"

class DimIndicador(MongoBaseModel):
    nome: str = Field(..., description="Nome do teste/indicador funcional")
    descricao: Optional[str] = Field(None, description="O que este teste avalia") 
    unidade_medida: str = Field(..., description="Ex: graus, cm, pontos, kg")
    direcao_melhora: DirecaoMelhora = Field(..., description="Define como o % de progresso é calculado")
    sem_limitacao_valor: bool = Field(default=True, description="Quando true, aceita qualquer valor numérico")
    limite_minimo: Optional[float] = Field(None, description="Valor mínimo aceito para preenchimento")
    limite_maximo: Optional[float] = Field(None, description="Valor máximo aceito para preenchimento")
    areas_vinculadas: List[str] = Field(default=["Todas"], description="Ex: ['Ortopedia', 'Neurologia']")
    is_ativo: bool = Field(default=True, description="Permite inativar sem excluir do histórico")
