from fastapi import APIRouter, Depends
from src.schemas.evolucao import EvolucaoCreate, EvolucaoResponse
from src.services import evolucao_service
from src.API.v1.routes.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=EvolucaoResponse)
async def create_evolucao(evolucao_in: EvolucaoCreate, current_user: dict = Depends(get_current_user)):
    return await evolucao_service.registrar_evolucao(evolucao_in, str(current_user["_id"]))