from pydantic import Field
from datetime import datetime, timezone
from src.models.base import MongoBaseModel, PyObjectId

class FatoMedicao(MongoBaseModel):
    evolucao_id: PyObjectId = Field(..., description="Referência à FatoEvolucao geradora")
    meta_smart_id: PyObjectId = Field(..., description="A qual meta essa aferição pertence")

    valor_anterior: float = Field(..., description="Resgatado da última medição desta meta pelo service")
    valor_medido: float = Field(..., description="O valor atual mensurado no dia do atendimento")
    data_medicao: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))