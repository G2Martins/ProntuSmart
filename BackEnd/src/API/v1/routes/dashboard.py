from fastapi import APIRouter, Depends
from src.core.security import get_current_user
from src.services import dashboard_service

router = APIRouter()


@router.get("/epidemiologia")
async def epidemiologia(current_user: dict = Depends(get_current_user)):
    """CIDs mais comuns por área e distribuição de pacientes."""
    return await dashboard_service.obter_epidemiologia()


@router.get("/produtividade")
async def produtividade(current_user: dict = Depends(get_current_user)):
    """Volume de evoluções por estagiário e totais gerais."""
    return await dashboard_service.obter_produtividade()


@router.get("/riscos")
async def riscos(current_user: dict = Depends(get_current_user)):
    """Pacientes com dor registrada ou metas estagnadas/atrasadas."""
    return await dashboard_service.obter_riscos()
