from pydantic import Field, EmailStr
from typing import Optional
from datetime import date
from enum import Enum
from src.models.base import MongoBaseModel

class AreaEspecializada(str, Enum):
    SAUDE_HOMEM_MULHER = "Saúde do Homem e da Mulher"
    GERIATRIA = "Geriatria"
    NEURO_ADULTO = "Neurologia Adulto"
    NEURO_PEDIATRIA = "Neuropediatria"
    ORTOPEDIA = "Ortopedia"
    PEDIATRIA = "Pediatria"

class SexoBiologico(str, Enum):
    MASCULINO = "Masculino"
    FEMININO = "Feminino"

class DimPaciente(MongoBaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF único do paciente")
    data_nascimento: date = Field(..., description="Data de nascimento para cálculo de idade")
    sexo: SexoBiologico
    telefone_contato: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = Field(default=None)
    endereco_resumido: Optional[str] = Field(default=None, max_length=200)
    
    # Informação clínica inicial
    area_atendimento_atual: AreaEspecializada = Field(..., description="Especialidade atual em que o paciente é atendido")
    queixa_principal: Optional[str] = Field(default=None, description="Identificação inicial da recepção/triagem")
    is_ativo: bool = Field(default=True, description="Define se o paciente está em atendimento ativo na clínica")