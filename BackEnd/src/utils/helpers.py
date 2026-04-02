from datetime import datetime
from src.models.dim_indicador import DirecaoMelhora

async def gerar_numero_prontuario(db) -> str:
    """
    Gera o número sequencial do prontuário no formato UCB-YYYY-XXXXX.
    """
    ano_atual = datetime.now().year
    
    # Busca o último prontuário criado no ano atual para descobrir a sequência
    ultimo_prontuario = await db.fato_prontuario.find_one(
        {"numero_prontuario": {"$regex": f"^UCB-{ano_atual}-"}},
        sort=[("numero_prontuario", -1)]
    )
    
    if ultimo_prontuario:
        # Pega a parte numérica final e soma 1
        sequencia = int(ultimo_prontuario["numero_prontuario"].split("-")[-1]) + 1
    else:
        # Se não houver nenhum no ano, começa do 1
        sequencia = 1
        
    return f"UCB-{ano_atual}-{sequencia:05d}"

def calcular_progresso(valor_inicial: float, valor_alvo: float, valor_atual: float, direcao: DirecaoMelhora) -> float:
    """
    Calcula o progresso percentual da meta respeitando a direção de melhora.
    """
    if valor_inicial == valor_alvo:
        return 100.0 if valor_atual == valor_alvo else 0.0
        
    if direcao == DirecaoMelhora.MAIOR_MELHOR:
        # Exemplo: Força Muscular. Inicial: 2, Alvo: 5, Atual: 3 -> Progresso de 33.3%
        if valor_atual <= valor_inicial:
            return 0.0
        if valor_atual >= valor_alvo:
            return 100.0
        progresso = ((valor_atual - valor_inicial) / (valor_alvo - valor_inicial)) * 100
        
    else: # DirecaoMelhora.MENOR_MELHOR
        # Exemplo: Escala de Dor (EVA). Inicial: 8, Alvo: 2, Atual: 5 -> Progresso de 50%
        if valor_atual >= valor_inicial:
            return 0.0
        if valor_atual <= valor_alvo:
            return 100.0
        progresso = ((valor_inicial - valor_atual) / (valor_inicial - valor_alvo)) * 100
        
    return round(progresso, 2)