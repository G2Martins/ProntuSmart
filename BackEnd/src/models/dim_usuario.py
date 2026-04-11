from datetime import datetime, timezone
from pydantic import ConfigDict, Field, EmailStr
from typing import Optional
from enum import Enum
from src.models.base import MongoBaseModel

class TipoPerfil(str, Enum):
    ESTAGIARIO = "Estagiario"
    DOCENTE = "Docente"
    ADMINISTRADOR = "Administrador"

class DimUsuario(MongoBaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150, description="Nome completo do usuário")
    matricula: str = Field(..., min_length=4, max_length=20, description="Matrícula(única)")
    email: EmailStr = Field(..., description="E-mail institucional ou pessoal")
    senha_hash: str = Field(..., description="Senha criptografada com bcrypt")
    perfil: TipoPerfil = Field(default=TipoPerfil.ESTAGIARIO, description="Nível de acesso no sistema")
    area_atendimento: Optional[str] = Field(default=None, description="Área de especialização (obrigatória para Estagiários)")
    is_ativo: bool = Field(default=True, description="Define se o usuário tem permissão de login")
    precisa_trocar_senha: bool = Field(default=False, description="Define se o usuário precisa trocar a senha ao fazer login")
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)