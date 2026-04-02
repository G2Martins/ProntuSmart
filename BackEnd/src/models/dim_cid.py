from pydantic import Field
from src.models.base import MongoBaseModel

class DimCid(MongoBaseModel):
    codigo: str = Field(..., min_length=3, max_length=10, description="Código CID-10 (ex: M54.5)")
    descricao: str = Field(..., description="Descrição da patologia")