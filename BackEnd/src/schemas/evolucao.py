from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from src.models.fato_evolucao import StatusEvolucao

class MedicaoItemSchema(BaseModel):
    indicador_id: str
    nome_indicador: str
    valor_registrado: str
    unidade: str

class EvolucaoCreate(BaseModel):
    prontuario_id: str
    texto_clinico: str = Field(..., min_length=10, description="Texto clínico da sessão (SOAP)")
    medicoes: List[MedicaoItemSchema] = Field(default=[], description="Indicadores medidos na sessão")

class EvolucaoResponse(BaseModel):
    id: str = Field(alias="_id")
    prontuario_id: str
    autor_id: str
    texto_clinico: str
    medicoes: List[MedicaoItemSchema] = []
    status: StatusEvolucao
    docente_revisor_id: Optional[str] = None
    feedback_docente: Optional[str] = None
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)