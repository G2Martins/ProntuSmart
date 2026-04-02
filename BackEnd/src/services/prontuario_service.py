from bson import ObjectId
from fastapi import HTTPException
from src.core.database import get_database
from src.schemas.prontuario import ProntuarioCreate
from src.models.fato_prontuario import FatoProntuario
# Importaremos de helpers na próxima etapa
from src.utils.helpers import gerar_numero_prontuario 

async def abrir_prontuario(prontuario_in: ProntuarioCreate) -> dict:
    db = get_database()
    
    # Verifica se o paciente existe
    paciente = await db.dim_paciente.find_one({"_id": ObjectId(prontuario_in.paciente_id)})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado para vínculo.")
        
    numero_gerado = await gerar_numero_prontuario(db)
    
    novo_prontuario = FatoProntuario(
        **prontuario_in.model_dump(),
        numero_prontuario=numero_gerado
    )
    
    resultado = await db.fato_prontuario.insert_one(novo_prontuario.model_dump(by_alias=True, exclude_none=True))
    return await db.fato_prontuario.find_one({"_id": resultado.inserted_id})

async def buscar_prontuario(prontuario_id: str) -> dict:
    db = get_database()
    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(prontuario_id)})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")
    return prontuario