from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime
import random

from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.models.fato_prontuario import FatoProntuario
from src.schemas.prontuario import ProntuarioCreate, ProntuarioResponse

router = APIRouter()

# RBAC: Só Docente Tria!
def verificar_docente(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.DOCENTE:
        raise HTTPException(status_code=403, detail="Apenas Docentes podem realizar a Triagem Clínica.")
    return current_user

@router.post("/", response_model=ProntuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_docente)])
async def criar_prontuario(prontuario_in: ProntuarioCreate, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    
    # Verifica se já existe um prontuário ativo para este paciente nesta área
    existente = await db.fato_prontuario.find_one({
        "paciente_id": prontuario_in.paciente_id,
        "area_atendimento": prontuario_in.area_atendimento,
        "status": "Ativo"
    })
    if existente:
        raise HTTPException(status_code=400, detail="Este paciente já tem um prontuário ativo nesta Área Clínica.")

    # Gera um número de prontuário amigável
    ano = datetime.now().year
    num_aleatorio = random.randint(1000, 9999)
    numero_gerado = f"PRONT-{ano}-{num_aleatorio}"

    dados = prontuario_in.model_dump()
    dados["docente_id"] = str(current_user["_id"])
    dados["numero_prontuario"] = numero_gerado

    novo_prontuario = FatoProntuario(**dados)
    resultado = await db.fato_prontuario.insert_one(novo_prontuario.model_dump(by_alias=True, exclude_none=True))
    
    prontuario_criado = await db.fato_prontuario.find_one({"_id": resultado.inserted_id})
    prontuario_criado["_id"] = str(prontuario_criado["_id"])
    return prontuario_criado

@router.get("/meus", response_model=List[ProntuarioResponse])
async def listar_meus_prontuarios(db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Vínculo: O Estagiário só vê os pacientes triados para ele.
    filtro = {}
    if current_user.get("perfil") == TipoPerfil.ESTAGIARIO:
        filtro["estagiario_id"] = str(current_user["_id"])
    
    cursor = db.fato_prontuario.find(filtro).sort("criado_em", -1)
    prontuarios = await cursor.to_list(length=200)
    for p in prontuarios: p["_id"] = str(p["_id"])
    return prontuarios

@router.get("/{id}", response_model=ProntuarioResponse)
async def buscar_prontuario(id: str, db = Depends(get_database)):
    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(id)})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")
    prontuario["_id"] = str(prontuario["_id"])
    return prontuario