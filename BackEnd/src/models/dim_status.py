from enum import Enum

class StatusMeta(str, Enum):
    NAO_INICIADA       = "Não iniciada"
    EM_ANDAMENTO       = "Em andamento"
    PARCIALMENTE       = "Parcialmente atingida"
    CONCLUIDA          = "Atingida"
    NAO_ATINGIDA       = "Não atingida"
    SUBSTITUIDA        = "Substituída"
    CANCELADA          = "Cancelada"

class StatusProntuario(str, Enum):
    ATIVO        = "Ativo"
    ALTA         = "Alta"
    ENCAMINHADO  = "Encaminhado"

class ProgressoMeta(str, Enum):
    SIM     = "Sim"
    NAO     = "Não"
    PARCIAL = "Parcial"

class CondicaoMeta(str, Enum):
    MANTIDA     = "Mantida"
    AJUSTADA    = "Ajustada"
    CONCLUIDA   = "Concluída"
    SUBSTITUIDA = "Substituída"
    SUSPENSA    = "Suspensa"