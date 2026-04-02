from fastapi import APIRouter, Depends
from src.schemas.medicao import MedicaoCreate, MedicaoResponse
from src.services import medicao_service
from src.API.v1.routes.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=MedicaoResponse)
async def create_medicao(medicao_in: MedicaoCreate, current_user: dict = Depends(get_current_user)):
    return await medicao_service.registrar_medicao(medicao_in)