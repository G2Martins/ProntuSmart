import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.services.auth_service import get_password_hash
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

    # 3. Povoar Docente Padrão (Administrador inicial)
    matricula_admin = "docente01"
    senha_plana = "ucb@1234"
    
    docente_base = {
        "nome_completo": "Docente Supervisor (Padrão)",
        "matricula": matricula_admin,
        "email": "docente.ucb@exemplo.com",
        "senha_hash": get_password_hash(senha_plana),
        "perfil": TipoPerfil.DOCENTE,
        "is_ativo": True,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc)
    }

    if await db.dim_usuario.count_documents({"matricula": matricula_admin}) == 0:
        await db.dim_usuario.insert_one(docente_base)
        print("✅ Docente padrão criado com sucesso!")
        print(f"   -> Matrícula: {matricula_admin}")
        print(f"   -> Senha: {senha_plana}")
    else:
        print("⚡ Docente padrão já existia no banco.")

    print("Finalizado!")
    client.close()

if __name__ == "__main__":
    # Roda a função assíncrona
    asyncio.run(rodar_seed())