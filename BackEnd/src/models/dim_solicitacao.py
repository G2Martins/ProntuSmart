from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import ConfigDict, EmailStr, Field

from src.models.base import MongoBaseModel
from src.models.dim_usuario import TipoPerfil


class StatusSolicitacao(str, Enum):
    PENDENTE = "Pendente"
    APROVADA = "Aprovada"
    RECUSADA = "Recusada"


class DimSolicitacaoCadastro(MongoBaseModel):
    """Solicitação pública de cadastro — passa por aprovação manual do Admin."""
    nome_completo:    str = Field(..., min_length=3, max_length=150)
    matricula:        str = Field(..., min_length=4, max_length=20)
    email:            EmailStr
    senha_hash:       str = Field(..., description="Senha já hasheada com bcrypt no cadastro")
    perfil_solicitado: TipoPerfil = Field(default=TipoPerfil.ESTAGIARIO)
    area_atendimento: Optional[str] = None
    justificativa:    Optional[str] = Field(default=None, max_length=500)

    status:           StatusSolicitacao = Field(default=StatusSolicitacao.PENDENTE)
    motivo_recusa:    Optional[str] = None
    revisado_por_id:  Optional[str] = None
    revisado_em:      Optional[datetime] = None

    criado_em:    datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
