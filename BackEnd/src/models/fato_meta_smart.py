from pydantic import Field
from datetime import datetime
from src.models.base import MongoBaseModel, PyObjectId
from src.models.dim_status import StatusMeta

class FatoMetaSmart(MongoBaseModel):
    prontuario_id: PyObjectId = Field(...)
    indicador_id: PyObjectId = Field(..., description="Referência ao DimIndicador")
    estagiario_id: PyObjectId = Field(..., description="Referência ao DimUsuario (quem criou)")

    # Estrutura SMART
    especifico: str = Field(..., description="O que será alcançado (S)")
    valor_inicial: float = Field(..., description="Base de cálculo inicial (M)")
    valor_alvo: float = Field(..., description="Aonde se quer chegar (M)")
    alcancavel: str = Field(..., description="Como a meta é realista para o caso (A)")
    relevante: str = Field(..., description="Importância funcional da meta (R)")
    data_limite: datetime = Field(..., description="Prazo para o atingimento (T)")

    status: StatusMeta = Field(default=StatusMeta.EM_ANDAMENTO)
    progresso_percentual: float = Field(default=0.0, description="Atualizado a cada medição nova")