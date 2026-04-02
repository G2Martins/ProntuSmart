from pydantic import Field, EmailStr
from enum import Enum
from src.models.base import MongoBaseModel

class TipoPerfil(str, Enum):
    ESTAGIARIO = "Estagiario"
    DOCENTE = "Docente"

class DimUsuario(MongoBaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150, description="Nome completo do usuário")
    matricula: str = Field(..., min_length=4, max_length=20, description="Matrícula(única)")
    email: EmailStr = Field(..., description="E-mail institucional ou pessoal")
    senha_hash: str = Field(..., description="Senha criptografada com bcrypt")
    perfil: TipoPerfil = Field(default=TipoPerfil.ESTAGIARIO, description="Nível de acesso no sistema")
    is_ativo: bool = Field(default=True, description="Define se o usuário tem permissão de login")