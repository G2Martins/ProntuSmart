from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from src.core.database import get_database
from src.schemas.meta_smart import MetaSmartCreate
from src.models.fato_meta_smart import FatoMetaSmart
from src.models.dim_status import StatusMeta

# Campos que NÃO podem ser editados (imutabilidade clínica)
CAMPOS_IMUTAVEIS = {"valor_inicial", "indicador_id", "prontuario_id", "estagiario_id",
                    "_id", "criado_em", "status", "progresso_percentual", "historico_alteracoes"}

def _serializar(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def criar_meta_smart(meta_in: MetaSmartCreate, estagiario_id: str) -> dict:
    db = get_database()
    nova_meta = FatoMetaSmart(**meta_in.model_dump(), estagiario_id=estagiario_id)
    resultado = await db.fato_meta_smart.insert_one(
        nova_meta.model_dump(by_alias=True, exclude_none=True)
    )
    criado = await db.fato_meta_smart.find_one({"_id": resultado.inserted_id})
    return _serializar(criado)

async def listar_metas_por_prontuario(prontuario_id: str) -> list:
    db = get_database()
    cursor = db.fato_meta_smart.find({"prontuario_id": prontuario_id})
    metas = await cursor.to_list(length=100)
    return [_serializar(m) for m in metas]

async def editar_meta(meta_id: str, dados: dict, usuario_id: str) -> dict:
    db = get_database()

    meta = await db.fato_meta_smart.find_one({"_id": ObjectId(meta_id)})
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada.")

    status_bloqueados = {StatusMeta.CANCELADA, StatusMeta.CONCLUIDA, StatusMeta.SUBSTITUIDA}
    if meta.get("status") in status_bloqueados:
        raise HTTPException(status_code=400, detail="Meta finalizada não pode ser editada.")

    # Remove campos imutáveis do payload
    campos_editaveis = {k: v for k, v in dados.items() if k not in CAMPOS_IMUTAVEIS}
    if not campos_editaveis:
        raise HTTPException(status_code=400, detail="Nenhum campo editável informado.")

    # Registra no histórico o que foi alterado
    entrada_historico = {
        "data":      datetime.now(timezone.utc).isoformat(),
        "usuario_id": usuario_id,
        "alteracoes": {k: {"de": meta.get(k), "para": v} for k, v in campos_editaveis.items()}
    }

    campos_editaveis["atualizado_em"] = datetime.now(timezone.utc)

    await db.fato_meta_smart.update_one(
        {"_id": ObjectId(meta_id)},
        {
            "$set":  campos_editaveis,
            "$push": {"historico_alteracoes": entrada_historico}
        }
    )
    atualizada = await db.fato_meta_smart.find_one({"_id": ObjectId(meta_id)})
    return _serializar(atualizada)

async def alterar_status_meta(meta_id: str, novo_status: str, motivo: str, usuario_id: str) -> dict:
    db = get_database()

    meta = await db.fato_meta_smart.find_one({"_id": ObjectId(meta_id)})
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada.")

    status_permitidos = {StatusMeta.CANCELADA, StatusMeta.SUBSTITUIDA, StatusMeta.NAO_ATINGIDA}
    if novo_status not in status_permitidos:
        raise HTTPException(status_code=400, detail=f"Status '{novo_status}' não é permitido nesta operação.")

    if not motivo.strip():
        raise HTTPException(status_code=400, detail="Motivo é obrigatório para encerrar uma meta.")

    entrada_historico = {
        "data":       datetime.now(timezone.utc).isoformat(),
        "usuario_id": usuario_id,
        "alteracoes": {"status": {"de": meta.get("status"), "para": novo_status}, "motivo": motivo}
    }

    await db.fato_meta_smart.update_one(
        {"_id": ObjectId(meta_id)},
        {
            "$set":  {"status": novo_status, "atualizado_em": datetime.now(timezone.utc)},
            "$push": {"historico_alteracoes": entrada_historico}
        }
    )
    atualizada = await db.fato_meta_smart.find_one({"_id": ObjectId(meta_id)})
    return _serializar(atualizada)