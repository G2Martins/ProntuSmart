from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from src.models.base import MongoBaseModel


class TipoRelatorio(str, Enum):
    PADRAO   = "Padrao"     # Modelo UCB (texto formal de uma página)
    COMPLETO = "Completo"   # Snapshot total: triagem + avaliação + evoluções + metas + indicadores


class StatusRelatorio(str, Enum):
    RASCUNHO              = "Rascunho"
    AGUARDANDO_DOCENTE    = "Aguardando Assinatura do Docente"
    FINALIZADO            = "Finalizado"
    CANCELADO             = "Cancelado"


class Assinatura(BaseModel):
    """Registro de assinatura digital — imutável após registrada."""
    usuario_id:      str
    nome_completo:   str
    matricula:       str
    perfil:          str  # "Estagiario" / "Docente"
    data_assinatura: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash_documento:  str  # SHA256 do conteúdo no momento da assinatura


class FatoRelatorio(MongoBaseModel):
    # ── Vínculos ──────────────────────────────────────────────
    prontuario_id: str = Field(..., description="Prontuário de origem")
    paciente_id:   str = Field(..., description="Paciente referenciado")
    estagiario_id: str = Field(..., description="Estagiário que solicitou")
    docente_id:    Optional[str] = Field(default=None, description="Docente vinculado")

    # ── Identificação ─────────────────────────────────────────
    numero_relatorio: str = Field(..., description="Ex: REL-2026-00001")
    tipo:             TipoRelatorio = Field(default=TipoRelatorio.PADRAO)
    status:           StatusRelatorio = Field(default=StatusRelatorio.RASCUNHO)

    # ── Conteúdo do Relatório PADRÃO (modelo UCB) ────────────
    diagnostico_clinico:           Optional[str] = None  # Ex: "neuropatia medicamentosa, parkinson..."
    queixa_principal:              Optional[str] = None  # Citação direta da queixa
    diagnostico_fisioterapeutico:  Optional[str] = None
    objetivos_tratamento:          Optional[str] = None
    atividades_realizadas:         Optional[str] = None
    observacoes_evolucao:          Optional[str] = None  # Ex: "não foi possível observar melhoras em..."
    consideracoes_finais:          Optional[str] = None

    # ── Snapshot completo (apenas para tipo COMPLETO) ─────────
    snapshot_completo: Optional[dict] = Field(default=None, description="Cópia imutável de todos dados clínicos no momento da emissão")

    # ── Assinaturas digitais ──────────────────────────────────
    assinatura_estagiario: Optional[Assinatura] = None
    assinatura_docente:    Optional[Assinatura] = None

    # ── Auditoria ─────────────────────────────────────────────
    data_emissao:    Optional[datetime] = None  # Set quando finalizado
    motivo_cancelamento: Optional[str]  = None
    hash_integridade: Optional[str]     = None  # SHA256 do conteúdo após finalização

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
