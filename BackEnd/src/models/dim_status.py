from enum import Enum

class StatusMeta(str, Enum):
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"
    ATRASADA = "Atrasada"
    CANCELADA = "Cancelada"

class StatusProntuario(str, Enum):
    ATIVO = "Ativo"
    ALTA = "Alta"
    ENCAMINHADO = "Encaminhado"