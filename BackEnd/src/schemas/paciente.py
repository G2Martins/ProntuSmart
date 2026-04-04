from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.dim_paciente import AreaEspecializada, SexoBiologico

class PacienteBase(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14)
    data_nascimento: str
    sexo: SexoBiologico
    telefone_contato: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    endereco_resumido: Optional[str] = Field(None, max_length=200)
    area_atendimento_atual: AreaEspecializada
    queixa_principal: Optional[str] = None
    is_ativo: bool = True

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    # CPF e Data de Nascimento geralmente não mudam após criados.
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=150)
    telefone_contato: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    endereco_resumido: Optional[str] = Field(None, max_length=200)
    area_atendimento_atual: Optional[AreaEspecializada] = None
    queixa_principal: Optional[str] = None
    is_ativo: Optional[bool] = None

class PacienteResponse(PacienteBase):
    id: str = Field(alias="_id")
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)