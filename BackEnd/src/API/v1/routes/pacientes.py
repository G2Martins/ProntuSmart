from fastapi import APIRouter, Depends
from typing import List
from src.schemas.paciente import PacienteCreate, PacienteResponse
from src.services import paciente_service
from src.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=PacienteResponse)
async def create_paciente(paciente_in: PacienteCreate, current_user: dict = Depends(get_current_user)):
    return await paciente_service.criar_paciente(paciente_in)

@router.get("/", response_model=List[PacienteResponse])
async def read_pacientes(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    return await paciente_service.listar_pacientes(skip=skip, limit=limit)

@router.get("/{id}", response_model=PacienteResponse)
async def read_paciente(id: str, current_user: dict = Depends(get_current_user)):
    return await paciente_service.buscar_paciente_por_id(id)