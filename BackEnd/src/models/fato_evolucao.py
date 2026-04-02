from pydantic import Field
from datetime import datetime, timezone
from src.models.base import MongoBaseModel, PyObjectId

class FatoEvolucao(MongoBaseModel):
    prontuario_id: PyObjectId = Field(...)
    estagiario_id: PyObjectId = Field(..., description="Estagiário que realizou o atendimento do dia")
    data_atendimento: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    observacoes_objetivas: str = Field(
        ..., 
        description="Descrição funcional do estado atual do paciente. PROIBIDO listar técnicas aplicadas."
    )