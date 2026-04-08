from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from src.core.database import get_database
from src.schemas.evolucao import EvolucaoCreate
from src.models.fato_evolucao import FatoEvolucao, MedicaoItem

async def registrar_evolucao(evolucao_in: EvolucaoCreate, autor_id: str) -> dict:
    db = get_database()

    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(evolucao_in.prontuario_id)})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")

    medicoes_modelo = [
        MedicaoItem(
            indicador_id=m.indicador_id,
            nome_indicador=m.nome_indicador,
            valor_registrado=m.valor_registrado,
            unidade=m.unidade
        ) for m in evolucao_in.medicoes
    ]

    nova_evolucao = FatoEvolucao(
        prontuario_id=evolucao_in.prontuario_id,
        autor_id=autor_id,
        texto_clinico=evolucao_in.texto_clinico,
        medicoes=medicoes_modelo
    )

    resultado = await db.fato_evolucao.insert_one(
        nova_evolucao.model_dump(by_alias=True, exclude_none=True)
    )

    await db.fato_prontuario.update_one(
        {"_id": ObjectId(evolucao_in.prontuario_id)},
        {
            "$inc": {"total_sessoes": 1},
            "$set": {"data_ultima_evolucao": datetime.now(timezone.utc)}
        }
    )

    criado = await db.fato_evolucao.find_one({"_id": resultado.inserted_id})
    criado["_id"] = str(criado["_id"])
    return criado

async def listar_por_prontuario(prontuario_id: str) -> list:
    db = get_database()
    cursor = db.fato_evolucao.find(
        {"prontuario_id": prontuario_id}
    ).sort("criado_em", -1)
    evolucoes = await cursor.to_list(length=200)
    for e in evolucoes:
        e["_id"] = str(e["_id"])
    return evolucoes