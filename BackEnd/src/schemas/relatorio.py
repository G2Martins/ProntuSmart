from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from src.models.fato_relatorio import TipoRelatorio, StatusRelatorio, Assinatura


class RelatorioCreate(BaseModel):
    """Cria um rascunho de relatório a partir de um prontuário."""
    prontuario_id: str
    tipo:          TipoRelatorio = TipoRelatorio.PADRAO
    # Conteúdo opcional na criação — pode ser preenchido depois
    diagnostico_clinico:          Optional[str] = None
    queixa_principal:             Optional[str] = None
    diagnostico_fisioterapeutico: Optional[str] = None
    objetivos_tratamento:         Optional[str] = None
    atividades_realizadas:        Optional[str] = None
    observacoes_evolucao:         Optional[str] = None
    consideracoes_finais:         Optional[str] = None


class RelatorioUpdate(BaseModel):
    """Atualiza conteúdo do rascunho. Só permitido enquanto status = Rascunho."""
    diagnostico_clinico:          Optional[str] = None
    queixa_principal:             Optional[str] = None
    diagnostico_fisioterapeutico: Optional[str] = None
    objetivos_tratamento:         Optional[str] = None
    atividades_realizadas:        Optional[str] = None
    observacoes_evolucao:         Optional[str] = None
    consideracoes_finais:         Optional[str] = None


class RelatorioAssinarRequest(BaseModel):
    """Confirmação de assinatura digital — exige senha do usuário corrente."""
    senha: str = Field(..., min_length=4, description="Senha do usuário para confirmar identidade")


class RelatorioResponse(BaseModel):
    id:               str = Field(alias="_id")
    prontuario_id:    str
    paciente_id:      str
    estagiario_id:    str
    docente_id:       Optional[str] = None
    numero_relatorio: str
    tipo:             TipoRelatorio
    status:           StatusRelatorio

    diagnostico_clinico:          Optional[str] = None
    queixa_principal:             Optional[str] = None
    diagnostico_fisioterapeutico: Optional[str] = None
    objetivos_tratamento:         Optional[str] = None
    atividades_realizadas:        Optional[str] = None
    observacoes_evolucao:         Optional[str] = None
    consideracoes_finais:         Optional[str] = None

    snapshot_completo: Optional[dict] = None

    assinatura_estagiario: Optional[Assinatura] = None
    assinatura_docente:    Optional[Assinatura] = None

    data_emissao:    Optional[datetime] = None
    hash_integridade: Optional[str] = None
    criado_em:       datetime

    # Campos enriquecidos
    nome_paciente:   Optional[str] = None
    nome_estagiario: Optional[str] = None
    nome_docente:    Optional[str] = None
    area_atendimento: Optional[str] = None
    numero_prontuario: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
