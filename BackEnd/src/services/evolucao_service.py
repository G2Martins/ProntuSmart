from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from src.core.database import get_database
from src.schemas.evolucao import EvolucaoCreate
from src.models.fato_evolucao import FatoEvolucao

async def registrar_evolucao(evolucao_in: EvolucaoCreate, estagiario_id: str) -> dict:
    db = get_database()
    
    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(evolucao_in.prontuario_id)})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")
        
    nova_evolucao = FatoEvolucao(
        **evolucao_in.model_dump(),
        estagiario_id=estagiario_id
    )
    
    resultado = await db.fato_evolucao.insert_one(nova_evolucao.model_dump(by_alias=True, exclude_none=True))
    
    # Atualiza o prontuário: incrementa sessões e atualiza a data da última evolução
    await db.fato_prontuario.update_one(
        {"_id": ObjectId(evolucao_in.prontuario_id)},
        {
            "$inc": {"total_sessoes": 1},
            "$set": {"data_ultima_evolucao": datetime.now(timezone.utc)}
        }
    )
    
    return await db.fato_evolucao.find_one({"_id": resultado.inserted_id})