from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from src.models.dim_status import ProgressoMeta, CondicaoMeta

class StatusEvolucao(str, Enum):
    PENDENTE_REVISAO = "Pendente de Revisão"
    APROVADO         = "Aprovado e Assinado"
    AJUSTES          = "Ajustes Solicitados"

class MedicaoItem(BaseModel):
    indicador_id:     str
    nome_indicador:   str
    valor_registrado: str
    unidade:          str

class FatoEvolucao(BaseModel):
    prontuario_id: str
    autor_id:      str
    medicoes:      List[MedicaoItem] = []

    # ── TELA 5: Campos de Reavaliação (novo — do documento) ──
    indicador_reavaliado: Optional[str] = None        # qual indicador foi mensurado
    valor_atual:          Optional[str] = None        # valor medido nesta sessão
    houve_progresso:      Optional[ProgressoMeta] = None  # Sim/Não/Parcial
    condicao_meta:        Optional[CondicaoMeta]  = None  # Mantida/Ajustada/...
    motivo_ajuste:        Optional[str] = None
    proxima_revisao:      Optional[datetime] = None

    # Aprovação
    status:              StatusEvolucao = Field(default=StatusEvolucao.PENDENTE_REVISAO)
    docente_revisor_id:  Optional[str]  = None
    feedback_docente:    Optional[str]  = None

    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
