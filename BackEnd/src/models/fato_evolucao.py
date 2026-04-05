from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum

class StatusEvolucao(str, Enum):
    PENDENTE_REVISAO = "Pendente de Revisão"
    APROVADO = "Aprovado e Assinado"
    AJUSTES = "Ajustes Solicitados"

# Sub-documento (As perguntas respondidas na hora)
class MedicaoItem(BaseModel):
    indicador_id: str
    nome_indicador: str
    valor_registrado: str
    unidade: str

class FatoEvolucao(BaseModel):
    prontuario_id: str
    autor_id: str # ID do Estagiário
    texto_clinico: str = Field(..., min_length=10)
    
    # A Mágica do MongoDB: As medições ficam guardadas junto com a evolução!
    medicoes: List[MedicaoItem] = []
    
    status: StatusEvolucao = Field(default=StatusEvolucao.PENDENTE_REVISAO)
    
    # Para a Fase 3 (Aprovação)
    docente_revisor_id: Optional[str] = None
    feedback_docente: Optional[str] = None
    
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)