from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.models.dim_cid import DimCid
from src.schemas.cid import CidCreate, CidUpdate, CidResponse

router = APIRouter()

# Middleware para garantir que só Admins manipulam CIDs
def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Administradores.")
    return current_user

@router.get("/", response_model=List[CidResponse])
async def listar_cids(db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Busca e ordena alfabeticamente pelo código
    cursor = db.dim_cid.find().sort("codigo", 1)
    cids = await cursor.to_list(length=1000) # Limite folgado, CIDs podem ser muitos
    for c in cids: c["_id"] = str(c["_id"])
    return cids

@router.post("/", response_model=CidResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_cid(cid_in: CidCreate, db = Depends(get_database)):
    if await db.dim_cid.find_one({"codigo": cid_in.codigo}):
        raise HTTPException(status_code=400, detail="Já existe um CID com este código.")
    
    novo_cid = DimCid(**cid_in.model_dump())
    resultado = await db.dim_cid.insert_one(novo_cid.model_dump(by_alias=True, exclude_none=True))
    cid_criado = await db.dim_cid.find_one({"_id": resultado.inserted_id})
    cid_criado["_id"] = str(cid_criado["_id"])
    return cid_criado

@router.put("/{cid_id}", response_model=CidResponse, dependencies=[Depends(verificar_admin)])
async def atualizar_cid(cid_id: str, cid_in: CidUpdate, db = Depends(get_database)):
    update_data = cid_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado para atualização.")
        
    res = await db.dim_cid.update_one({"_id": ObjectId(cid_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="CID não encontrado.")
        
    cid = await db.dim_cid.find_one({"_id": ObjectId(cid_id)})
    cid["_id"] = str(cid["_id"])
    return cid