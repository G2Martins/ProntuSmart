from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class EvolucaoBase(BaseModel):
    observacoes_objetivas: str = Field(
        ..., 
        description="Apenas evolução funcional. Condutas e técnicas são vetadas."
    )

class EvolucaoCreate(EvolucaoBase):
    prontuario_id: str
    # estagiario_id e data_atendimento serão injetados pelo backend

class EvolucaoResponse(EvolucaoBase):
    id: str = Field(alias="_id")
    prontuario_id: str
    estagiario_id: str
    data_atendimento: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)