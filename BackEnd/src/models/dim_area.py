from pydantic import Field
from src.models.base import MongoBaseModel

class DimArea(MongoBaseModel):
    nome: str = Field(..., description="Nome da área especializada (ex: Ortopedia)")
    descricao: str = Field(default="", description="Descrição detalhada da área")
    is_ativo: bool = Field(default=True)