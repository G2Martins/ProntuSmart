from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from src.core.database import get_database
from src.schemas.meta_smart import MetaSmartCreate
from src.models.fato_meta_smart import FatoMetaSmart

def _serializar(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def criar_meta_smart(meta_in: MetaSmartCreate, estagiario_id: str) -> dict:
    db = get_database()

    if meta_in.data_limite.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="A data limite deve ser no futuro.")

    nova_meta = FatoMetaSmart(
        **meta_in.model_dump(),
        estagiario_id=estagiario_id
    )

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