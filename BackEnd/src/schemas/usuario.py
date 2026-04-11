from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.dim_usuario import TipoPerfil

class UsuarioBase(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    matricula: str = Field(..., min_length=4, max_length=20)
    email: EmailStr
    perfil: TipoPerfil = TipoPerfil.ESTAGIARIO
    is_ativo: bool = True

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, description="Senha em texto plano que será hasheada no service")

class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    perfil: Optional[TipoPerfil] = None
    is_ativo: Optional[bool] = None

class UsuarioResponse(BaseModel):
    id: str = Field(alias="_id")
    nome_completo: str
    matricula: str
    email: EmailStr
    perfil: TipoPerfil
    is_ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)