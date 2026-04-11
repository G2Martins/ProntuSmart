from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from src.models.dim_status import StatusMeta

class MetaSmartBase(BaseModel):
    indicador_id:       str
    especifico:         str
    valor_inicial:      float
    valor_alvo:         float
    alcancavel:         str
    relevante:          str
    data_limite:        datetime
    # Campos novos do documento clínico
    problema_relacionado: Optional[str] = None
    criterio_mensuravel:  Optional[str] = None
    condicao_execucao:    Optional[str] = None
    data_reavaliacao:     Optional[datetime] = None

class MetaSmartCreate(MetaSmartBase):
    prontuario_id: str

class MetaSmartResponse(MetaSmartBase):
    id:                   str = Field(alias="_id")
    prontuario_id:        str
    estagiario_id:        str
    status:               StatusMeta
    progresso_percentual: float
    criado_em:            datetime
    atualizado_em:        Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)