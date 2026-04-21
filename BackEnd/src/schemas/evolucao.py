from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class MedicaoItemSchema(BaseModel):
    indicador_id:     str
    nome_indicador:   str
    valor_registrado: str
    unidade:          str

class EvolucaoCreate(BaseModel):
    prontuario_id:       str
    medicoes:            List[MedicaoItemSchema] = []
    # Campos de reavaliação de meta (opcionais)
    meta_id_reavaliada:  Optional[str]      = None  # ← ID da meta que está sendo reavaliada
    indicador_reavaliado: Optional[str]     = None
    valor_atual:         Optional[str]      = None
    houve_progresso:     Optional[str]      = None
    condicao_meta:       Optional[str]      = None
    motivo_ajuste:       Optional[str]      = None
    proxima_revisao:     Optional[datetime] = None

class EvolucaoResponse(BaseModel):
    id:                  str = Field(alias="_id")
    prontuario_id:       str
    autor_id:            str
    medicoes:            List[MedicaoItemSchema] = []
    status:              str
    indicador_reavaliado: Optional[str]     = None
    valor_atual:         Optional[str]      = None
    houve_progresso:     Optional[str]      = None
    condicao_meta:       Optional[str]      = None
    motivo_ajuste:       Optional[str]      = None
    proxima_revisao:     Optional[datetime] = None
    feedback_docente:    Optional[str]      = None
    docente_revisor_id:  Optional[str]      = None
    criado_em:           datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
