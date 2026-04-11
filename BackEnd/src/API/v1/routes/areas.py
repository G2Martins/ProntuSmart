from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.models.dim_area import DimArea
from src.schemas.area import AreaCreate, AreaUpdate, AreaResponse

router = APIRouter()

# Middleware para garantir que só Admins criam/editam áreas
def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Administradores.")
    return current_user

@router.get("/", response_model=List[AreaResponse])
async def listar_areas(db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Qualquer usuário logado pode ver as áreas, mas podemos filtrar se necessário
    cursor = db.dim_area.find().sort("nome", 1)
    areas = await cursor.to_list(length=100)
    for a in areas: a["_id"] = str(a["_id"])
    return areas

@router.post("/", response_model=AreaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_area(area_in: AreaCreate, db = Depends(get_database)):
    if await db.dim_area.find_one({"nome": area_in.nome}):
        raise HTTPException(status_code=400, detail="Já existe uma área com este nome.")
    
    nova_area = DimArea(**area_in.model_dump())
    resultado = await db.dim_area.insert_one(nova_area.model_dump(by_alias=True, exclude_none=True))
    area_criada = await db.dim_area.find_one({"_id": resultado.inserted_id})
    area_criada["_id"] = str(area_criada["_id"])
    return area_criada

@router.put("/{area_id}", response_model=AreaResponse, dependencies=[Depends(verificar_admin)])
async def atualizar_area(area_id: str, area_in: AreaUpdate, db = Depends(get_database)):
    update_data = area_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado para atualização")
        
    res = await db.dim_area.update_one({"_id": ObjectId(area_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Área não encontrada")
        
    area = await db.dim_area.find_one({"_id": ObjectId(area_id)})
    area["_id"] = str(area["_id"])
    return area