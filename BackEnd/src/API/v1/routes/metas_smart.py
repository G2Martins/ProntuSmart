from fastapi import APIRouter, Depends
from typing import List
from src.schemas.meta_smart import MetaSmartCreate, MetaSmartResponse
from src.services import meta_smart_service
from src.API.v1.routes.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=MetaSmartResponse)
async def create_meta(meta_in: MetaSmartCreate, current_user: dict = Depends(get_current_user)):
    # Passamos o ID do estagiário logado para o serviço
    return await meta_smart_service.criar_meta_smart(meta_in, str(current_user["_id"]))

@router.get("/prontuario/{prontuario_id}", response_model=List[MetaSmartResponse])
async def read_metas_prontuario(prontuario_id: str, current_user: dict = Depends(get_current_user)):
    return await meta_smart_service.listar_metas_por_prontuario(prontuario_id)