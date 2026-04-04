from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import List
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.schemas.indicador import IndicadorCreate, IndicadorUpdate, IndicadorResponse
from src.services import indicador_service

router = APIRouter()

def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Funcionalidade exclusiva para Administradores."
        )
    return current_user

@router.get("/", response_model=List[IndicadorResponse])
async def listar_indicadores(
    apenas_ativos: bool = Query(False),
    _: dict = Depends(get_current_user)
):
    return await indicador_service.listar_indicadores(apenas_ativos)

@router.get("/{indicador_id}", response_model=IndicadorResponse)
async def buscar_indicador(
    indicador_id: str,
    _: dict = Depends(get_current_user)
):
    return await indicador_service.buscar_indicador_por_id(indicador_id)

@router.post("/", response_model=IndicadorResponse, status_code=201)
async def criar_indicador(
    indicador_in: IndicadorCreate,
    _: dict = Depends(verificar_admin)
):
    return await indicador_service.criar_indicador(indicador_in)

@router.put("/{indicador_id}", response_model=IndicadorResponse)
async def atualizar_indicador(
    indicador_id: str,
    indicador_in: IndicadorUpdate,
    _: dict = Depends(verificar_admin)
):
    return await indicador_service.atualizar_indicador(indicador_id, indicador_in)

@router.delete("/{indicador_id}", status_code=204)
async def deletar_indicador(
    indicador_id: str,
    _: dict = Depends(verificar_admin)
):
    await indicador_service.deletar_indicador(indicador_id)