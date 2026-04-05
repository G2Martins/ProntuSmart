from pydantic import Field, ConfigDict
from datetime import datetime, timezone
from typing import Optional
from src.models.base import MongoBaseModel
from src.models.dim_status import StatusProntuario

class FatoProntuario(MongoBaseModel):
    paciente_id: str = Field(..., description="Referência ao DimPaciente")
    estagiario_id: str = Field(..., description="Estagiário responsável pelo atendimento")
    docente_id: str = Field(..., description="Docente que realizou a triagem")
    cid_id: str = Field(..., description="CID principal associado ao tratamento")
    area_atendimento: str = Field(..., description="Área clínica (ex: Ortopedia)")
    
    numero_prontuario: str = Field(..., description="Gerado automaticamente (ex: PRONT-2026-1234)")
    status: StatusProntuario = Field(default=StatusProntuario.ATIVO)
    
    total_sessoes: int = Field(default=0)
    data_ultima_evolucao: Optional[datetime] = None
    resumo_avaliacao_inicial: str = Field(default="Triagem inicial realizada pelo docente.")
    
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)