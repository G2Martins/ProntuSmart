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

async def contar_pendentes_por_docente(docente_id: str) -> int:
    """Conta evoluções 'Pendente de Revisão' nos prontuários deste docente."""
    db = get_database()
    prontuarios = await db.fato_prontuario.find(
        {"docente_id": docente_id}
    ).to_list(length=1000)

    if not prontuarios:
        return 0

    prontuario_ids = [str(p["_id"]) for p in prontuarios]

    count = await db.fato_evolucao.count_documents({
        "prontuario_id": {"$in": prontuario_ids},
        "status": "Pendente de Revisão"
    })
    return count

async def revisar_evolucao(evolucao_id: str, docente_id: str, acao: str, feedback: str | None) -> dict:
    db = get_database()

    evolucao = await db.fato_evolucao.find_one({"_id": ObjectId(evolucao_id)})
    if not evolucao:
        raise HTTPException(status_code=404, detail="Evolução não encontrada.")

    if evolucao.get("status") != "Pendente de Revisão":
        raise HTTPException(status_code=400, detail="Esta evolução já foi revisada.")

    # Valida que o docente é responsável pelo prontuário
    prontuario = await db.fato_prontuario.find_one({
        "_id": ObjectId(evolucao["prontuario_id"]),
        "docente_id": docente_id
    })
    if not prontuario:
        raise HTTPException(status_code=403, detail="Você não é responsável por este prontuário.")

    if acao == "aprovar":
        novo_status = "Aprovado e Assinado"
    elif acao == "devolver":
        if not feedback:
            raise HTTPException(status_code=400, detail="Feedback obrigatório ao devolver.")
        novo_status = "Ajustes Solicitados"
    else:
        raise HTTPException(status_code=400, detail="Ação inválida. Use 'aprovar' ou 'devolver'.")

    await db.fato_evolucao.update_one(
        {"_id": ObjectId(evolucao_id)},
        {"$set": {
            "status":             novo_status,
            "docente_revisor_id": docente_id,
            "feedback_docente":   feedback,
            "atualizado_em":      datetime.now(timezone.utc)
        }}
    )

    atualizada = await db.fato_evolucao.find_one({"_id": ObjectId(evolucao_id)})
    atualizada["_id"] = str(atualizada["_id"])
    return atualizada

async def listar_pendentes_por_docente(docente_id: str) -> list:
    db = get_database()
    prontuarios = await db.fato_prontuario.find(
        {"docente_id": docente_id}
    ).to_list(length=1000)

    if not prontuarios:
        return []

    ids = [str(p["_id"]) for p in prontuarios]

    cursor = db.fato_evolucao.find({
        "prontuario_id": {"$in": ids},
        "status": "Pendente de Revisão"
    }).sort("criado_em", 1)  # Mais antigas primeiro

    pendentes = await cursor.to_list(length=200)
    for e in pendentes:
        e["_id"] = str(e["_id"])
    return pendentes