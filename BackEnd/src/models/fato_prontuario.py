from pydantic import Field
from datetime import datetime
from typing import Optional
from src.models.base import MongoBaseModel, PyObjectId
from src.models.dim_status import StatusProntuario

class FatoProntuario(MongoBaseModel):
    paciente_id: PyObjectId = Field(..., description="Referência ao DimPaciente")
    numero_prontuario: str = Field(..., description="Gerado via helpers (ex: UCB-2026-00001)")
    status: StatusProntuario = Field(default=StatusProntuario.ATIVO)
    
    # Atualizados via serviços dinamicamente
    total_sessoes: int = Field(default=0)
    data_ultima_evolucao: Optional[datetime] = None
    
    area_id: PyObjectId = Field(..., description="Área atual de tratamento na clínica")
    resumo_avaliacao_inicial: str = Field(..., description="Contextualização clínica base, sem prescrever conduta")