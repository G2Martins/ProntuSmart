from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime
import random

from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.models.fato_prontuario import FatoProntuario
from src.schemas.prontuario import ProntuarioCreate, ProntuarioAvaliacaoUpdate, ProntuarioResponse

router = APIRouter()

def verificar_docente(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") not in [TipoPerfil.DOCENTE, TipoPerfil.ADMINISTRADOR]:
        raise HTTPException(status_code=403, detail="Apenas Docentes podem realizar a Triagem.")
    return current_user

@router.post("/", response_model=ProntuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_prontuario(
    prontuario_in: ProntuarioCreate,
    db = Depends(get_database),
    current_user: dict = Depends(verificar_docente)
):
    existente = await db.fato_prontuario.find_one({
        "paciente_id": prontuario_in.paciente_id,
        "area_atendimento": prontuario_in.area_atendimento,
        "status": "Ativo"
    })
    if existente:
        raise HTTPException(status_code=400, detail="Este paciente já possui um prontuário ativo nesta área.")

    num_aleatorio = random.randint(1000, 9999)
    numero_gerado = f"UCB-{datetime.now().year}-{num_aleatorio:04d}"

    dados = prontuario_in.model_dump()
    dados["docente_id"] = str(current_user["_id"])
    dados["numero_prontuario"] = numero_gerado

    novo = FatoProntuario(**dados)
    resultado = await db.fato_prontuario.insert_one(novo.model_dump(by_alias=True, exclude_none=True))

    criado = await db.fato_prontuario.find_one({"_id": resultado.inserted_id})
    criado["_id"] = str(criado["_id"])
    return criado

@router.patch("/{id}/avaliacao", response_model=ProntuarioResponse)
async def atualizar_avaliacao_funcional(
    id: str,
    dados_in: ProntuarioAvaliacaoUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Tela 2 + Tela 3 — Estagiário preenche avaliação funcional e síntese."""
    update_data = dados_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado.")

    update_data["atualizado_em"] = datetime.utcnow()
    res = await db.fato_prontuario.update_one(
        {"_id": ObjectId(id)}, {"$set": update_data}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")

    pront = await db.fato_prontuario.find_one({"_id": ObjectId(id)})
    pront["_id"] = str(pront["_id"])
    return pront

@router.get("/meus", response_model=List[ProntuarioResponse])
async def listar_meus_prontuarios(db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    filtro = {}
    if current_user.get("perfil") == TipoPerfil.ESTAGIARIO:
        filtro["estagiario_id"] = str(current_user["_id"])
    elif current_user.get("perfil") == TipoPerfil.DOCENTE:
        filtro["docente_id"] = str(current_user["_id"])

    cursor = db.fato_prontuario.find(filtro).sort("criado_em", -1)
    prontuarios = await cursor.to_list(length=200)
    for p in prontuarios:
        p["_id"] = str(p["_id"])
    return prontuarios

@router.get("/paciente/{paciente_id}", response_model=ProntuarioResponse)
async def buscar_prontuario_por_paciente(paciente_id: str, db = Depends(get_database)):
    prontuario = await db.fato_prontuario.find_one({"paciente_id": paciente_id, "status": "Ativo"})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Este paciente ainda não possui triagem/prontuário ativo.")
    prontuario["_id"] = str(prontuario["_id"])
    return prontuario

@router.get("/{prontuario_id}")
async def buscar_prontuario(
    prontuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    from bson import ObjectId
    pront = await db.fato_prontuario.find_one({"_id": ObjectId(prontuario_id)})
    if not pront:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")
    pront["_id"] = str(pront["_id"])
    return pront