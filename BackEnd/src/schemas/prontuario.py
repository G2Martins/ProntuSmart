from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.dim_status import StatusProntuario

class ProntuarioBase(BaseModel):
    paciente_id: str
    area_id: str
    resumo_avaliacao_inicial: str

class ProntuarioCreate(ProntuarioBase):
    pass

class ProntuarioResponse(ProntuarioBase):
    id: str = Field(alias="_id")
    numero_prontuario: str
    status: StatusProntuario
    total_sessoes: int
    data_ultima_evolucao: Optional[datetime]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)