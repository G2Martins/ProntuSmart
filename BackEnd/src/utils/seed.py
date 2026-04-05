import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.dim_usuario import TipoPerfil
from src.models.dim_indicador import DirecaoMelhora

async def rodar_seed():
    print("Iniciando o povoamento do banco de dados (Seed)...")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # ==========================================
    # 1. ÁREAS DE ATENDIMENTO
    # ==========================================
    areas_base = [
        {
            "nome": "Saúde da Mulher e do Homem", 
            "descricao": "Fisioterapia pélvica e saúde preventiva", 
            "icone": "ph:person-simple-walk-bold",
            "cor": "rose",
            "is_ativo": True, 
            "criado_em": datetime.now(timezone.utc), 
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Geriatria", 
            "descricao": "Saúde do idoso e prevenção de quedas", 
            "icone": "ph:wheelchair-bold",
            "cor": "amber",
            "is_ativo": True, 
            "criado_em": datetime.now(timezone.utc), 
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Neurologia Adulto", 
            "descricao": "Reabilitação neurofuncional para adultos", 
            "icone": "ph:brain-bold",
            "cor": "purple",
            "is_ativo": True, 
            "criado_em": datetime.now(timezone.utc), 
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Neuropediatria", 
            "descricao": "Reabilitação neurofuncional pediátrica", 
            "icone": "ph:baby-bold",
            "cor": "cyan",
            "is_ativo": True, 
            "criado_em": datetime.now(timezone.utc), 
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Traumato-Ortopedia", 
            "descricao": "Reabilitação de fraturas e lesões", 
            "icone": "ph:bone-bold",
            "cor": "blue",
            "is_ativo": True, 
            "criado_em": datetime.now(timezone.utc), 
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Cardiorrespiratória", 
            "descricao": "Reabilitação cardíaca e pulmonar", 
            "icone": "ph:lungs-bold",
            "cor": "emerald",
            "is_ativo": True, 
            "criado_em": datetime.now(timezone.utc), 
            "atualizado_em": datetime.now(timezone.utc)
        }
    ]

    for area in areas_base:
        if await db.dim_area.count_documents({"nome": area["nome"]}) == 0:
            await db.dim_area.insert_one(area)
            print(f"✅ Área cadastrada: {area['nome']}")

    # ==========================================
    # 2. INDICADORES FUNCIONAIS (CORRIGIDO)
    # ==========================================
    indicadores_base = [
        {
            "nome": "Escala Visual Analógica (EVA)",
            "unidade_medida": "pontos (0-10)",
            "direcao_melhora": DirecaoMelhora.MENOR_MELHOR,
            "descricao": "Mede a intensidade da dor do paciente.",
            "areas_vinculadas": ["Todas"], # <-- ADICIONADO
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Time Up and Go (TUG)",
            "unidade_medida": "segundos",
            "direcao_melhora": DirecaoMelhora.MENOR_MELHOR,
            "descricao": "Avalia mobilidade, equilíbrio e risco de quedas.",
            "areas_vinculadas": ["Geriatria", "Neurologia Adulto"], # <-- ADICIONADO
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc)
        },
        {
            "nome": "Força Muscular (Grau 0-5)",
            "unidade_medida": "grau",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "descricao": "Graduação da força muscular.",
            "areas_vinculadas": ["Ortopedia", "Traumato-Ortopedia", "Neurologia Adulto"], # <-- ADICIONADO
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc)
        }
    ]

    for ind in indicadores_base:
        if await db.dim_indicador.count_documents({"nome": ind["nome"]}) == 0:
            await db.dim_indicador.insert_one(ind)
            print(f"✅ Indicador cadastrado: {ind['nome']}")

    # ==========================================
    # 3. USUÁRIOS BASE
    # ==========================================
    senha_hash = get_password_hash("ucb@1234")

    admin_base = {
        "nome_completo": "Administrador Sistema",
        "matricula": "admin01",
        "email": "admin.ucb@exemplo.com",
        "senha_hash": senha_hash,
        "perfil": TipoPerfil.ADMINISTRADOR,
        "is_ativo": True,
        "precisa_trocar_senha": False,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc),
    }

    docente_base = {
        "nome_completo": "Docente Supervisor",
        "matricula": "docente01",
        "email": "docente.ucb@exemplo.com",
        "senha_hash": senha_hash,
        "perfil": TipoPerfil.DOCENTE,
        "is_ativo": True,
        "precisa_trocar_senha": False,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc),
    }

    estagiario_base = {
        "nome_completo": "Estagiário Padrão",
        "matricula": "estagiario01",
        "email": "estagiario.ucb@exemplo.com",
        "senha_hash": senha_hash,
        "perfil": TipoPerfil.ESTAGIARIO,
        "is_ativo": True,
        "precisa_trocar_senha": False,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc),
    }

    if await db.dim_usuario.count_documents({"matricula": "admin01"}) == 0:
        await db.dim_usuario.insert_one(admin_base)
        print("✅ Administrador padrão criado! (admin01 / ucb@1234)")

    if await db.dim_usuario.count_documents({"matricula": "docente01"}) == 0:
        await db.dim_usuario.insert_one(docente_base)
        print("✅ Docente padrão criado! (docente01 / ucb@1234)")

    if await db.dim_usuario.count_documents({"matricula": "estagiario01"}) == 0:
        await db.dim_usuario.insert_one(estagiario_base)
        print("✅ Estagiário padrão criado! (estagiario01 / ucb@1234)")

    print("🚀 Seed finalizado com sucesso!")
    client.close()

if __name__ == "__main__":
    asyncio.run(rodar_seed())