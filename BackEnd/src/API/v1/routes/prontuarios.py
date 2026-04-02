from fastapi import APIRouter, Depends
from src.schemas.prontuario import ProntuarioCreate, ProntuarioResponse
from src.services import prontuario_service
from src.API.v1.routes.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ProntuarioResponse)
async def create_prontuario(prontuario_in: ProntuarioCreate, current_user: dict = Depends(get_current_user)):
    return await prontuario_service.abrir_prontuario(prontuario_in)

@router.get("/{id}", response_model=ProntuarioResponse)
async def read_prontuario(id: str, current_user: dict = Depends(get_current_user)):
    return await prontuario_service.buscar_prontuario(id)