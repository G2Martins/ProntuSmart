from pydantic import Field
from datetime import datetime
from typing import Optional, List
from src.models.base import MongoBaseModel, PyObjectId
from src.models.dim_status import StatusMeta

class HistoricoAlteracaoMeta(MongoBaseModel):
    """Rastreia cada vez que uma meta é substituída ou ajustada."""
    meta_anterior_descricao: str
    status_final:            StatusMeta
    motivo_alteracao:        str
    nova_meta_id:            Optional[PyObjectId] = None
    data_alteracao:          datetime = Field(default_factory=datetime.utcnow)

class FatoMetaSmart(MongoBaseModel):
    prontuario_id:  PyObjectId = Field(...)
    indicador_id:   PyObjectId = Field(..., description="Referência ao DimIndicador")
    estagiario_id:  PyObjectId = Field(..., description="Quem criou a meta")

    # Contexto clínico (novo — do documento)
    problema_relacionado: Optional[str] = Field(None, description="Ex: Déficit de marcha")

    # Estrutura SMART
    especifico:          str   = Field(..., description="S — O que será alcançado")
    criterio_mensuravel: Optional[str] = Field(None, description="M — Critério em texto (ex: Caminhar 10 metros)")
    valor_inicial:       float = Field(..., description="M — Base numérica")
    valor_alvo:          float = Field(..., description="M — Alvo numérico")
    condicao_execucao:   Optional[str] = Field(None, description="A — Condição/adaptação (ex: Com andador e supervisão)")
    alcancavel:          str   = Field(..., description="A — Por que é realista")
    relevante:           str   = Field(..., description="R — Importância funcional")
    data_limite:         datetime = Field(..., description="T — Prazo")

    status:               StatusMeta = Field(default=StatusMeta.NAO_INICIADA)
    progresso_percentual: float      = Field(default=0.0)

    # Histórico de alterações (novo)
    historico_alteracoes: List[HistoricoAlteracaoMeta] = Field(default=[])

    data_reavaliacao: Optional[datetime] = None