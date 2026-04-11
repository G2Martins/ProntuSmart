from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone

class DimCid(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=10, description="Código CID, ex: M54.5")
    descricao: str = Field(..., min_length=3, max_length=255, description="Descrição da patologia")
    is_ativo: bool = Field(default=True)
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)