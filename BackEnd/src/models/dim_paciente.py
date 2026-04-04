from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import date, datetime, timezone
from enum import Enum

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

class DimPaciente(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF único do paciente")
    data_nascimento: date = Field(..., description="Data de nascimento para cálculo de idade")
    sexo: SexoBiologico
    telefone_contato: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    endereco_resumido: Optional[str] = Field(default=None, max_length=200)
    
    # Informação clínica inicial
    area_atendimento_atual: AreaEspecializada
    queixa_principal: Optional[str] = None
    
    # Controle de Sistema
    is_ativo: bool = Field(default=True)
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)