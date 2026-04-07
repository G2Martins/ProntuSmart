from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.dim_status import StatusProntuario

class ProntuarioCreate(BaseModel):
    paciente_id: str
    estagiario_id: str
    cid_id: str
    area_atendimento: str

class ProntuarioResponse(ProntuarioCreate):
    id: str = Field(alias="_id")
    docente_id: str
    numero_prontuario: str
    status: StatusProntuario
    total_sessoes: int
    data_ultima_evolucao: Optional[datetime] = None
    resumo_avaliacao_inicial: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)