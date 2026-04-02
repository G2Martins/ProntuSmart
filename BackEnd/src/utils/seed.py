import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.dim_usuario import TipoPerfil
from src.models.dim_indicador import DirecaoMelhora

async def rodar_seed():
    print("Iniciando o povoamento do banco de dados (Seed)...")
    
    # Conecta ao MongoDB diretamente para o script isolado
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # 1. Povoar Áreas Especializadas
    areas_base = [
        {"nome": "Saúde do Homem e da Mulher", "descricao": "Fisioterapia pélvica e saúde preventiva", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Geriatria", "descricao": "Saúde do idoso e prevenção de quedas", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Neurologia Adulto", "descricao": "Reabilitação neurofuncional para adultos", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Neuropediatria", "descricao": "Reabilitação neurofuncional pediátrica", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Ortopedia", "descricao": "Reabilitação traumato-ortopédica", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Pediatria", "descricao": "Fisioterapia pediátrica e desenvolvimento motor", "is_ativo": True, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)}
    ]
    
    if await db.dim_area.count_documents({}) == 0:
        await db.dim_area.insert_many(areas_base)
        print("✅ Áreas de especialidade populadas com sucesso!")
    else:
        print("⚡ Áreas de especialidade já existiam no banco.")

    # 2. Povoar Indicadores Fisioterapêuticos (Exemplos)
    indicadores_base = [
        {"nome": "Escala Visual Analógica de Dor (EVA)", "unidade_medida": "pontos (0-10)", "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Força Muscular (Escala de Oxford)", "unidade_medida": "graus (0-5)", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Amplitude de Movimento (Goniometria)", "unidade_medida": "graus (°)", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)},
        {"nome": "Timed Up and Go (TUG)", "unidade_medida": "segundos", "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "criado_em": datetime.now(timezone.utc), "atualizado_em": datetime.now(timezone.utc)}
    ]

    if await db.dim_indicador.count_documents({}) == 0:
        await db.dim_indicador.insert_many(indicadores_base)
        print("✅ Indicadores funcionais (testes) populados com sucesso!")
    else:
        print("⚡ Indicadores funcionais já existiam no banco.")

    # 3. Povoar Administrador e Docente Padrão
    senha_plana = "ucb@1234"
    senha_hash = get_password_hash(senha_plana)
    
    # Criando o Super Admin
    admin_base = {
        "nome_completo": "Administrador do Sistema",
        "matricula": "admin01",
        "email": "admin.ti@ucb.br",
        "senha_hash": senha_hash,
        "perfil": TipoPerfil.ADMINISTRADOR,
        "is_ativo": True,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc)
    }

    # Criando o Docente
    docente_base = {
        "nome_completo": "Docente Supervisor",
        "matricula": "docente01",
        "email": "docente.ucb@exemplo.com",
        "senha_hash": senha_hash,
        "perfil": TipoPerfil.DOCENTE,
        "is_ativo": True,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc)
    }

    # Inserindo no banco caso não existam
    if await db.dim_usuario.count_documents({"matricula": "admin01"}) == 0:
        await db.dim_usuario.insert_one(admin_base)
        print("✅ Administrador padrão criado! (admin01 / ucb@1234)")
        
    if await db.dim_usuario.count_documents({"matricula": "docente01"}) == 0:
        await db.dim_usuario.insert_one(docente_base)
        print("✅ Docente padrão criado! (docente01 / ucb@1234)")

    print("Finalizado!")
    client.close()

if __name__ == "__main__":
    # Roda a função assíncrona
    asyncio.run(rodar_seed())