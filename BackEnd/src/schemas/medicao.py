from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MedicaoBase(BaseModel):
    valor_medido: float

class MedicaoCreate(MedicaoBase):
    evolucao_id: str
    meta_smart_id: str

class MedicaoResponse(MedicaoBase):
    id: str = Field(alias="_id")
    evolucao_id: str
    meta_smart_id: str
    valor_anterior: float
    data_medicao: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)