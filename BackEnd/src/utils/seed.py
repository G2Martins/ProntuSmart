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

    # 1. Áreas Especializadas
    areas_base = [
        {"nome": "Saúde do Homem e da Mulher", "descricao": "Fisioterapia pélvica e saúde preventiva", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Geriatria", "descricao": "Saúde do idoso e prevenção de quedas", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Neurologia Adulto", "descricao": "Reabilitação neurofuncional para adultos", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Neuropediatria", "descricao": "Reabilitação neurofuncional pediátrica", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Ortopedia", "descricao": "Reabilitação traumato-ortopédica", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Pediatria", "descricao": "Fisioterapia pediátrica e desenvolvimento motor", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
    ]

    if await db.dim_area.count_documents({}) == 0:
        await db.dim_area.insert_many(areas_base)
        print("✅ Áreas de especialidade populadas com sucesso!")
    else:
        print("⚡ Áreas de especialidade já existiam no banco.")

    # 2. Indicadores Fisioterapêuticos
    indicadores_base = [
        {
            "nome": "Escala Visual Analógica de Dor (EVA)",
            "descricao": "Avalia a intensidade da dor percebida pelo paciente em uma escala de 0 (sem dor) a 10 (pior dor imaginável).",
            "unidade_medida": "pontos (0-10)",
            "direcao_melhora": DirecaoMelhora.MENOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Força Muscular (Escala de Oxford)",
            "descricao": "Gradua a força muscular de 0 (sem contração) a 5 (força normal contra resistência total).",
            "unidade_medida": "graus (0-5)",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Amplitude de Movimento (Goniometria)",
            "descricao": "Mede a amplitude de movimento articular em graus por meio de um goniômetro.",
            "unidade_medida": "graus (°)",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Timed Up and Go (TUG)",
            "descricao": "Avalia mobilidade funcional e risco de queda. Mede o tempo para levantar, caminhar 3m, voltar e sentar.",
            "unidade_medida": "segundos",
            "direcao_melhora": DirecaoMelhora.MENOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Escala de Equilíbrio de Berg",
            "descricao": "Avalia o equilíbrio funcional em 14 tarefas do dia a dia, com pontuação de 0 a 56.",
            "unidade_medida": "pontos (0-56)",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Teste de Caminhada de 6 Minutos (TC6)",
            "descricao": "Mede a distância máxima percorrida em 6 minutos, avaliando a capacidade funcional aeróbica.",
            "unidade_medida": "metros",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Índice de Barthel",
            "descricao": "Avalia a independência funcional nas atividades básicas de vida diária, de 0 (dependência total) a 100 (independência total).",
            "unidade_medida": "pontos (0-100)",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
        {
            "nome": "Dinamometria (Força de Preensão)",
            "descricao": "Mede a força de preensão palmar em quilograma-força (kgf) com uso de dinamômetro.",
            "unidade_medida": "kgf",
            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR,
            "is_ativo": True,
            "criado_em": datetime.now(timezone.utc),
            "atualizado_em": datetime.now(timezone.utc),
        },
    ]

    if await db.dim_indicador.count_documents({}) == 0:
        await db.dim_indicador.insert_many(indicadores_base)
        print("✅ Indicadores funcionais populados com sucesso!")
    else:
        print("⚡ Indicadores funcionais já existiam no banco.")

    # 3. Usuários Padrão
    senha_hash = get_password_hash("ucb@1234")

    admin_base = {
        "nome_completo": "Administrador do Sistema",
        "matricula": "admin01",
        "email": "admin.ti@ucb.br",
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

    print("\n🎉 Seed finalizado com sucesso!")
    client.close()

if __name__ == "__main__":
    asyncio.run(rodar_seed())