from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timezone

from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.models.dim_paciente import DimPaciente
from src.schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse

router = APIRouter()

# SEGURANÇA: Apenas Admins e Docentes podem criar/editar pacientes.
def verificar_criacao(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") not in [TipoPerfil.ADMINISTRADOR, TipoPerfil.DOCENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas Docentes e Administradores podem cadastrar pacientes."
        )
    return current_user

@router.get("/", response_model=List[PacienteResponse])
async def listar_pacientes(skip: int = 0, limit: int = 100, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Qualquer utilizador logado (incluindo estagiário) pode listar pacientes
    cursor = db.dim_paciente.find().sort("nome_completo", 1).skip(skip).limit(limit)
    pacientes = await cursor.to_list(length=limit)
    for p in pacientes: 
        p["_id"] = str(p["_id"])
    return pacientes

@router.get("/{paciente_id}", response_model=PacienteResponse)
async def buscar_paciente(paciente_id: str, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    paciente = await db.dim_paciente.find_one({"_id": ObjectId(paciente_id)})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    paciente["_id"] = str(paciente["_id"])
    return paciente

@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_criacao)])
async def criar_paciente(paciente_in: PacienteCreate, db = Depends(get_database)):
    # Impede duplicação de CPF
    if await db.dim_paciente.find_one({"cpf": paciente_in.cpf}):
        raise HTTPException(status_code=400, detail="Já existe um paciente cadastrado com este CPF.")
    
    novo_paciente = DimPaciente(**paciente_in.model_dump())
    resultado = await db.dim_paciente.insert_one(novo_paciente.model_dump(by_alias=True, exclude_none=True))
    
    paciente_criado = await db.dim_paciente.find_one({"_id": resultado.inserted_id})
    paciente_criado["_id"] = str(paciente_criado["_id"])
    return paciente_criado

@router.patch("/{paciente_id}", response_model=PacienteResponse, dependencies=[Depends(verificar_criacao)])
async def atualizar_paciente(paciente_id: str, paciente_in: PacienteUpdate, db = Depends(get_database)):
    update_data = paciente_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado para atualização.")
        
    update_data["atualizado_em"] = datetime.now(timezone.utc)
        
    res = await db.dim_paciente.update_one({"_id": ObjectId(paciente_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
        
    paciente = await db.dim_paciente.find_one({"_id": ObjectId(paciente_id)})
    paciente["_id"] = str(paciente["_id"])
    return paciente