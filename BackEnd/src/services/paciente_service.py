from bson import ObjectId
from fastapi import HTTPException
from src.core.database import get_database
from src.schemas.paciente import PacienteCreate, PacienteUpdate
from src.models.dim_paciente import DimPaciente

async def criar_paciente(paciente_in: PacienteCreate) -> dict:
    db = get_database()
    
    # Verifica se o CPF já está cadastrado
    if await db.dim_paciente.find_one({"cpf": paciente_in.cpf}):
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")
        
    novo_paciente = DimPaciente(**paciente_in.model_dump())
    resultado = await db.dim_paciente.insert_one(novo_paciente.model_dump(by_alias=True, exclude_none=True))
    
    return await db.dim_paciente.find_one({"_id": resultado.inserted_id})

async def listar_pacientes(skip: int = 0, limit: int = 100):
    db = get_database()
    cursor = db.dim_paciente.find({"is_ativo": True}).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

async def buscar_paciente_por_id(paciente_id: str) -> dict:
    db = get_database()
    paciente = await db.dim_paciente.find_one({"_id": ObjectId(paciente_id)})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente