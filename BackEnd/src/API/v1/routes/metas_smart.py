from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.schemas.meta_smart import MetaSmartCreate, MetaSmartResponse
from src.services import meta_smart_service
from src.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=MetaSmartResponse)
async def create_meta(meta_in: MetaSmartCreate, current_user: dict = Depends(get_current_user)):
    return await meta_smart_service.criar_meta_smart(meta_in, str(current_user["_id"]))

@router.get("/prontuario/{prontuario_id}", response_model=List[MetaSmartResponse])
async def read_metas_prontuario(prontuario_id: str, current_user: dict = Depends(get_current_user)):
    return await meta_smart_service.listar_metas_por_prontuario(prontuario_id)

@router.patch("/{meta_id}")
async def editar_meta(
    meta_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    """Edita campos permitidos de uma meta SMART."""
    return await meta_smart_service.editar_meta(meta_id, body, str(current_user["_id"]))

@router.patch("/{meta_id}/status")
async def cancelar_meta(
    meta_id: str,
    body: dict,  # { "status": "Cancelada", "motivo": "..." }
    current_user: dict = Depends(get_current_user)
):
    """Cancela ou marca como substituída uma meta SMART (soft delete clínico)."""
    status_novo: str = body.get("status") or ""
    motivo: str      = body.get("motivo") or ""

    if not status_novo:
        raise HTTPException(status_code=400, detail="Campo 'status' é obrigatório.")

    return await meta_smart_service.alterar_status_meta(
        meta_id=meta_id,
        novo_status=status_novo,
        motivo=motivo,
        usuario_id=str(current_user["_id"])
    )