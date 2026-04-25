from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.dim_solicitacao import StatusSolicitacao
from src.models.dim_usuario import TipoPerfil


class SolicitacaoCreate(BaseModel):
    """Payload público para criar uma solicitação de cadastro."""
    nome_completo:     str = Field(..., min_length=3, max_length=150)
    matricula:         str = Field(..., min_length=4, max_length=20)
    email:             EmailStr
    senha:             str = Field(..., min_length=6)
    perfil_solicitado: TipoPerfil = TipoPerfil.ESTAGIARIO
    area_atendimento:  Optional[str] = None
    justificativa:     Optional[str] = Field(default=None, max_length=500)


class SolicitacaoAprovar(BaseModel):
    """Admin pode editar campos antes de aprovar."""
    nome_completo:     Optional[str] = None
    email:             Optional[EmailStr] = None
    perfil_solicitado: Optional[TipoPerfil] = None
    area_atendimento:  Optional[str] = None


class SolicitacaoRecusar(BaseModel):
    motivo_recusa: str = Field(..., min_length=3, max_length=500)


class SolicitacaoResponse(BaseModel):
    id:                str = Field(alias="_id")
    nome_completo:     str
    matricula:         str
    email:             EmailStr
    perfil_solicitado: TipoPerfil
    area_atendimento:  Optional[str] = None
    justificativa:     Optional[str] = None
    status:            StatusSolicitacao
    motivo_recusa:     Optional[str] = None
    criado_em:         datetime
    revisado_em:       Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
