from fastapi import APIRouter, Depends
from typing import List
from src.schemas.evolucao import EvolucaoCreate, EvolucaoResponse
from src.services import evolucao_service
from src.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=EvolucaoResponse)
async def create_evolucao(
    evolucao_in: EvolucaoCreate,
    current_user: dict = Depends(get_current_user)
):
    return await evolucao_service.registrar_evolucao(evolucao_in, str(current_user["_id"]))

@router.get("/prontuario/{prontuario_id}", response_model=List[EvolucaoResponse])
async def listar_evolucoes_prontuario(
    prontuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await evolucao_service.listar_por_prontuario(prontuario_id)