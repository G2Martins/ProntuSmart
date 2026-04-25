from pydantic import Field, ConfigDict
from datetime import datetime, timezone
from typing import Optional, Union
from src.models.base import MongoBaseModel
from src.models.dim_status import StatusProntuario

# ── Tela 2: Avaliação Funcional ──────────────────────────────

class AvaliacaoMobilidade(ConfigDict):
    pass

class FatoProntuario(MongoBaseModel):
    # ── Vínculo e controle ────────────────────────────────────
    paciente_id:        str = Field(..., description="Referência ao DimPaciente")
    estagiario_id:      str = Field(..., description="Estagiário responsável")
    docente_id:         Optional[str] = Field(default=None, description="Docente responsável (atribuído posteriormente)")
    cid_id:             str = Field(..., description="CID principal")
    area_atendimento:   str = Field(..., description="Área clínica")
    numero_prontuario:  str = Field(..., description="Ex: UCB-2026-00001")
    status:             StatusProntuario = Field(default=StatusProntuario.ATIVO)
    total_sessoes:      int = Field(default=0)
    data_ultima_evolucao: Optional[datetime] = None

    # ── TELA 2: Avaliação Funcional — Mobilidade ─────────────
    sedestacao:    Optional[str] = None  # "Independente","Com apoio","Dependente"
    ortostatismo:  Optional[str] = None  # "Independente","Supervisão","Ajuda física","Não realiza"
    transferencias: Optional[str] = None # "Independente","Supervisão","Ajuda parcial","Dependente"

    # Marcha
    realiza_marcha:      Optional[Union[str, bool]] = None
    marcha_dispositivo:  Optional[bool] = None
    marcha_dispositivo_descricao: Optional[str] = None
    distancia_tolerada:  Optional[str]  = None

    # Função
    funcao_mmss:  Optional[str] = None  # "Preservada","Parcialmente comprometida","Comprometida"
    funcao_mmii:  Optional[str] = None
    equilibrio:   Optional[str] = None  # "Preservado","Alterado"
    risco_queda:  Optional[str] = None  # "Baixo","Moderado","Alto"

    # Sintomas
    dor:                  Optional[bool] = None
    dor_intensidade_local: Optional[str] = None
    fadiga_funcional:     Optional[bool] = None

    # Cognição / Comunicação
    compreende_comandos:      Optional[bool] = None
    comunicacao_preservada:   Optional[bool] = None
    # Coordenação
    coordenacao_decomposicao_movimentos: Optional[bool] = None
    coordenacao_ataxia_cerebelar: Optional[bool] = None
    coordenacao_dismetria: Optional[bool] = None
    coordenacao_nistagmo: Optional[bool] = None
    coordenacao_rechaco_stewart_holmes: Optional[bool] = None

    # AVDs: I=Independente, S=Supervisão, AP=Ajuda parcial, D=Dependente
    avd_banho:        Optional[str] = None
    avd_vestir:       Optional[str] = None
    avd_higiene:      Optional[str] = None
    avd_locomocao:    Optional[str] = None
    avd_alimentacao:  Optional[str] = None
    avd_banheiro:     Optional[str] = None

    # ── TELA 3: Síntese Fisioterapêutica ─────────────────────
    problema_funcional_prioritario: Optional[str] = None
    atividade_comprometida:         Optional[str] = None
    impacto_independencia:          Optional[str] = None
    prioridade_terapeutica:         Optional[str] = None

    criado_em:     datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
