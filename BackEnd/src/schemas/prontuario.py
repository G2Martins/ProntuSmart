from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.dim_status import StatusProntuario

class ProntuarioCreate(BaseModel):
    """Dados mínimos para abrir triagem (Estagiário). estagiario_id é preenchido pelo servidor."""
    paciente_id:      str
    cid_id:           str
    area_atendimento: str
    # Dados clínicos iniciais opcionais na triagem
    diagnostico_medico:           Optional[str] = None
    diagnostico_fisioterapeutico: Optional[str] = None
    queixa_principal:             Optional[str] = None
    objetivo_paciente:            Optional[str] = None
    tempo_evolucao:               Optional[str] = None
    comorbidades:                 Optional[str] = None
    medicamentos:                 Optional[str] = None
    dispositivo_auxiliar:         Optional[str] = None
    barreiras_ambientais:         Optional[str] = None

class ProntuarioAvaliacaoUpdate(BaseModel):
    """Atualiza Tela 2 (Avaliação Funcional) e Tela 3 (Síntese)."""
    # Mobilidade
    sedestacao:     Optional[str] = None
    ortostatismo:   Optional[str] = None
    transferencias: Optional[str] = None
    # Marcha
    realiza_marcha:     Optional[bool] = None
    marcha_dispositivo: Optional[bool] = None
    distancia_tolerada: Optional[str]  = None
    # Função
    funcao_mmss: Optional[str] = None
    funcao_mmii: Optional[str] = None
    equilibrio:  Optional[str] = None
    risco_queda: Optional[str] = None
    # Sintomas
    dor:                   Optional[bool] = None
    dor_intensidade_local: Optional[str]  = None
    fadiga_funcional:      Optional[bool] = None
    # Cognição
    compreende_comandos:    Optional[bool] = None
    comunicacao_preservada: Optional[bool] = None
    # AVDs
    avd_banho:       Optional[str] = None
    avd_vestir:      Optional[str] = None
    avd_higiene:     Optional[str] = None
    avd_locomocao:   Optional[str] = None
    avd_alimentacao: Optional[str] = None
    avd_banheiro:    Optional[str] = None
    # Participação
    atividade_mais_impactada: Optional[str] = None
    principal_limitacao:      Optional[str] = None
    teste_escala_principal:   Optional[str] = None
    valor_teste_inicial:      Optional[str] = None
    # Síntese (Tela 3)
    problema_funcional_prioritario: Optional[str] = None
    atividade_comprometida:         Optional[str] = None
    impacto_independencia:          Optional[str] = None
    prioridade_terapeutica:         Optional[str] = None

class ProntuarioResponse(BaseModel):
    id:               str = Field(alias="_id")
    paciente_id:      str
    estagiario_id:    str
    docente_id:       Optional[str] = None
    cid_id:           str
    # Campos enriquecidos (populados pelo endpoint /meus)
    nome_paciente:    Optional[str] = None
    nome_estagiario:  Optional[str] = None
    area_atendimento: str
    numero_prontuario: str
    status:            StatusProntuario
    total_sessoes:     int
    data_ultima_evolucao: Optional[datetime] = None

    # Tela 1
    diagnostico_medico:           Optional[str] = None
    diagnostico_fisioterapeutico: Optional[str] = None
    queixa_principal:             Optional[str] = None
    objetivo_paciente:            Optional[str] = None
    tempo_evolucao:               Optional[str] = None
    comorbidades:                 Optional[str] = None
    medicamentos:                 Optional[str] = None
    dispositivo_auxiliar:         Optional[str] = None
    barreiras_ambientais:         Optional[str] = None

    # Tela 2
    sedestacao: Optional[str] = None
    ortostatismo: Optional[str] = None
    transferencias: Optional[str] = None
    realiza_marcha: Optional[bool] = None
    marcha_dispositivo: Optional[bool] = None
    distancia_tolerada: Optional[str] = None
    funcao_mmss: Optional[str] = None
    funcao_mmii: Optional[str] = None
    equilibrio: Optional[str] = None
    risco_queda: Optional[str] = None
    dor: Optional[bool] = None
    dor_intensidade_local: Optional[str] = None
    fadiga_funcional: Optional[bool] = None
    compreende_comandos: Optional[bool] = None
    comunicacao_preservada: Optional[bool] = None
    avd_banho: Optional[str] = None
    avd_vestir: Optional[str] = None
    avd_higiene: Optional[str] = None
    avd_locomocao: Optional[str] = None
    avd_alimentacao: Optional[str] = None
    avd_banheiro: Optional[str] = None
    atividade_mais_impactada: Optional[str] = None
    principal_limitacao: Optional[str] = None
    teste_escala_principal: Optional[str] = None
    valor_teste_inicial: Optional[str] = None

    # Tela 3
    problema_funcional_prioritario: Optional[str] = None
    atividade_comprometida: Optional[str] = None
    impacto_independencia: Optional[str] = None
    prioridade_terapeutica: Optional[str] = None

    criado_em: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)