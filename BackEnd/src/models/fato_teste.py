from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import ConfigDict, Field

from src.models.base import MongoBaseModel


class TipoTeste(str, Enum):
    AVALIACAO_FUNCIONAL = "AvaliacaoFuncional"
    SUNNY               = "Sunny"
    MINI_BEST           = "MiniBest"


class FatoTeste(MongoBaseModel):
    """Registro genérico de teste/escala aplicada ao paciente em um prontuário."""
    prontuario_id:   str = Field(..., description="Prontuário ao qual o teste pertence")
    paciente_id:     str = Field(..., description="Paciente avaliado")
    aplicador_id:    str = Field(..., description="Usuário que aplicou (estagiário)")
    tipo:            TipoTeste

    # Conteúdo específico do teste — schema livre por tipo
    dados:           dict = Field(default_factory=dict)

    # Resumo numérico (preenchido quando aplicável)
    pontuacao_total:   Optional[float] = None
    pontuacao_maxima:  Optional[float] = None
    interpretacao:     Optional[str]   = None
    observacoes:       Optional[str]   = None

    data_aplicacao:    datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    criado_em:         datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em:     datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
