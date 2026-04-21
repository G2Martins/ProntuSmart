from bson import ObjectId
from datetime import datetime, timezone
from fastapi import HTTPException
from src.core.database import get_database
from src.schemas.indicador import IndicadorCreate, IndicadorUpdate
from src.models.dim_indicador import DimIndicador
from src.services.indicador_limits import normalizar_configuracao_limites

def _serializar(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
        doc.setdefault("sem_limitacao_valor", True)
        doc.setdefault("limite_minimo", None)
        doc.setdefault("limite_maximo", None)
    return doc

async def listar_indicadores(apenas_ativos: bool = False) -> list:
    db = get_database()
    filtro = {"is_ativo": True} if apenas_ativos else {}
    cursor = db.dim_indicador.find(filtro).sort("nome", 1)
    docs = await cursor.to_list(length=200)
    return [_serializar(doc) for doc in docs]

async def buscar_indicador_por_id(indicador_id: str) -> dict:
    db = get_database()
    indicador = await db.dim_indicador.find_one({"_id": ObjectId(indicador_id)})
    if not indicador:
        raise HTTPException(status_code=404, detail="Indicador não encontrado.")
    return _serializar(indicador)

async def criar_indicador(indicador_in: IndicadorCreate) -> dict:
    db = get_database()

    existente = await db.dim_indicador.find_one(
        {"nome": {"$regex": f"^{indicador_in.nome}$", "$options": "i"}}
    )
    if existente:
        raise HTTPException(status_code=400, detail="Já existe um indicador com este nome.")

    dados = normalizar_configuracao_limites(indicador_in.model_dump())
    novo = DimIndicador(**dados)
    resultado = await db.dim_indicador.insert_one(
        novo.model_dump(by_alias=True, exclude_none=True)
    )
    criado = await db.dim_indicador.find_one({"_id": resultado.inserted_id})
    return _serializar(criado)

async def atualizar_indicador(indicador_id: str, indicador_in: IndicadorUpdate) -> dict:
    db = get_database()
    existente = await db.dim_indicador.find_one({"_id": ObjectId(indicador_id)})
    if not existente:
        raise HTTPException(status_code=404, detail="Indicador não encontrado.")

    dados = {k: v for k, v in indicador_in.model_dump().items() if v is not None}
    if not dados:
        raise HTTPException(status_code=400, detail="Nenhum dado válido enviado.")

    dados = normalizar_configuracao_limites(dados, existente)
    dados["atualizado_em"] = datetime.now(timezone.utc)

    resultado = await db.dim_indicador.update_one(
        {"_id": ObjectId(indicador_id)},
        {"$set": dados}
    )
    atualizado = await db.dim_indicador.find_one({"_id": ObjectId(indicador_id)})
    return _serializar(atualizado)

async def deletar_indicador(indicador_id: str) -> bool:
    db = get_database()
    resultado = await db.dim_indicador.delete_one({"_id": ObjectId(indicador_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Indicador não encontrado.")
    return True
