"""
Seed enxuta do ProntuSMART.

Coleções limpas:
- dim_usuario, dim_area, dim_indicador
- dim_paciente, fato_prontuario, fato_meta_smart
- fato_evolucao, fato_medicao, fato_relatorio, fato_teste
- dim_solicitacao_cadastro

Coleção PRESERVADA:
- dim_cid (base oficial de 14k registros)

Cenário criado:
- 1 Administrador
- 1 Preceptor — Velluma (Neurologia Adulto)
- 1 Estagiária — Emellyn Lima (Neurologia Adulto)
- Áreas e indicadores cadastrados
- NENHUM paciente / prontuário / evolução
"""
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.dim_usuario import TipoPerfil
from src.models.dim_indicador import DirecaoMelhora


async def rodar_seed():
    print("Iniciando seed enxuta do ProntuSMART...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # ── Limpa coleções — dim_cid PRESERVADA ─────────────────────────────────
    colecoes = [
        "dim_usuario", "dim_area", "dim_indicador",
        "dim_paciente", "fato_prontuario", "fato_meta_smart",
        "fato_evolucao", "fato_medicao", "fato_relatorio", "fato_teste",
        "dim_solicitacao_cadastro",
    ]
    for col in colecoes:
        await db[col].drop()
        print(f"  - Coleção '{col}' limpa")
    print("  - dim_cid preservada (base oficial mantida)")

    agora = datetime.now(timezone.utc)

    # ────────────────────────────────────────────────────────────────────────
    # 1. ÁREAS DE ATENDIMENTO
    # ────────────────────────────────────────────────────────────────────────
    areas = [
        {"nome": "Saúde do Homem e da Mulher", "descricao": "Fisioterapia pélvica e saúde preventiva", "icone": "ph:person-simple-walk-bold", "cor": "rose",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Geriatria",                  "descricao": "Saúde do idoso e prevenção de quedas",     "icone": "ph:wheelchair-bold",         "cor": "amber",   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Neurologia Adulto",          "descricao": "Reabilitação neurofuncional para adultos", "icone": "ph:brain-bold",              "cor": "purple",  "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Neuropediatria",             "descricao": "Reabilitação neurofuncional pediátrica",   "icone": "ph:baby-bold",               "cor": "cyan",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Traumato-Ortopedia",         "descricao": "Reabilitação de fraturas e lesões",        "icone": "ph:bone-bold",               "cor": "blue",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Cardiorrespiratória",        "descricao": "Reabilitação cardíaca e pulmonar",         "icone": "ph:lungs-bold",              "cor": "emerald", "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for a in areas:
        await db.dim_area.insert_one(a)
    print(f"  + {len(areas)} Áreas cadastradas")

    # ────────────────────────────────────────────────────────────────────────
    # 2. INDICADORES CLÍNICOS
    # ────────────────────────────────────────────────────────────────────────
    indicadores = [
        {"nome": "Escala Visual Analógica (EVA)", "unidade_medida": "pontos (0-10)", "direcao_melhora": DirecaoMelhora.MENOR_MELHOR,
         "descricao": "Intensidade da dor relatada pelo paciente.",
         "areas_vinculadas": ["Todas"],
         "limite_minimo": 0, "limite_maximo": 10,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Escala de Berg", "unidade_medida": "pontos (0-56)", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Avalia equilíbrio funcional — ≤45 indica risco de queda.",
         "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],
         "limite_minimo": 0, "limite_maximo": 56,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Time Up and Go (TUG)", "unidade_medida": "segundos", "direcao_melhora": DirecaoMelhora.MENOR_MELHOR,
         "descricao": "Avalia mobilidade, equilíbrio e risco de quedas.",
         "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],
         "limite_minimo": 0, "limite_maximo": 120,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Distância de Marcha", "unidade_medida": "metros", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Distância percorrida com ou sem dispositivo auxiliar.",
         "areas_vinculadas": ["Geriatria", "Neurologia Adulto", "Traumato-Ortopedia"],
         "limite_minimo": 0, "limite_maximo": 1000,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Tempo em Ortostatismo Estável", "unidade_medida": "segundos", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Tempo em pé sem perda de equilíbrio.",
         "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],
         "limite_minimo": 0, "limite_maximo": 600,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Força Muscular (MRC 0-5)", "unidade_medida": "grau", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Graduação da força muscular por grupo muscular.",
         "areas_vinculadas": ["Traumato-Ortopedia", "Neurologia Adulto"],
         "limite_minimo": 0, "limite_maximo": 5,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Amplitude de Movimento (ADM)", "unidade_medida": "graus", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Amplitude articular em goniometria.",
         "areas_vinculadas": ["Traumato-Ortopedia"],
         "limite_minimo": 0, "limite_maximo": 360,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "SpO2 em Repouso", "unidade_medida": "%", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Saturação periférica de oxigênio.",
         "areas_vinculadas": ["Cardiorrespiratória"],
         "limite_minimo": 70, "limite_maximo": 100,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Mini-BESTest (Total)", "unidade_medida": "pontos (0-28)", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
         "descricao": "Pontuação total do Mini-BESTest. Cutoff de queda: ≤19.",
         "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],
         "limite_minimo": 0, "limite_maximo": 28,
         "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for indicador in indicadores:
        await db.dim_indicador.insert_one(indicador)
    print(f"  + {len(indicadores)} Indicadores cadastrados")

    # ────────────────────────────────────────────────────────────────────────
    # 3. USUÁRIOS — Admin + Velluma (Preceptor) + Emellyn (Estagiária)
    # ────────────────────────────────────────────────────────────────────────
    senha_hash = get_password_hash("ucb@1234")

    usuarios = [
        {
            "nome_completo": "Administrador Sistema",
            "matricula": "admin01",
            "email": "admin@ucb.br",
            "senha_hash": senha_hash,
            "perfil": TipoPerfil.ADMINISTRADOR,
            "area_atendimento": None,
            "is_ativo": True,
            "precisa_trocar_senha": False,
            "criado_em": agora,
            "atualizado_em": agora,
        },
        {
            "nome_completo": "Velluma",
            "matricula": "prec01",
            "email": "velluma@ucb.br",
            "senha_hash": senha_hash,
            "perfil": TipoPerfil.DOCENTE,
            "area_atendimento": "Neurologia Adulto",
            "is_ativo": True,
            "precisa_trocar_senha": False,
            "criado_em": agora,
            "atualizado_em": agora,
        },
        {
            "nome_completo": "Emellyn Lima",
            "matricula": "est01",
            "email": "emellyn.lima@ucb.br",
            "senha_hash": senha_hash,
            "perfil": TipoPerfil.ESTAGIARIO,
            "area_atendimento": "Neurologia Adulto",
            "is_ativo": True,
            "precisa_trocar_senha": False,
            "criado_em": agora,
            "atualizado_em": agora,
        },
    ]
    for u in usuarios:
        await db.dim_usuario.insert_one(u)
    print(f"  + {len(usuarios)} Usuários cadastrados")
    print("    - admin01 / ucb@1234  (Administrador)")
    print("    - prec01  / ucb@1234  (Preceptor — Velluma · Neurologia Adulto)")
    print("    - est01   / ucb@1234  (Estagiária — Emellyn Lima · Neurologia Adulto)")

    print("\nSeed concluída. Banco populado apenas com áreas, indicadores e 3 usuários.")
    print("Nenhum paciente / prontuário / relatório foi criado.")
    client.close()


if __name__ == "__main__":
    asyncio.run(rodar_seed())
