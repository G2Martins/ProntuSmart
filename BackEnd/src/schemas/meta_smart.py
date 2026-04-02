from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from src.models.dim_status import StatusMeta

class MetaSmartBase(BaseModel):
    indicador_id: str
    especifico: str
    valor_inicial: float
    valor_alvo: float
    alcancavel: str
    relevante: str
    data_limite: datetime

class MetaSmartCreate(MetaSmartBase):
    prontuario_id: str
    # estagiario_id será pego do token JWT pelo endpoint, não precisa vir do front

class MetaSmartResponse(MetaSmartBase):
    id: str = Field(alias="_id")
    prontuario_id: str
    estagiario_id: str
    status: StatusMeta
    progresso_percentual: float
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)