from fastapi import APIRouter, Depends, HTTPException, status
from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from src.services import auth_service
import asyncio
import secrets
import string
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.core.security import get_password_hash

router = APIRouter()

def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Funcionalidade exclusiva para Administradores."
        )
    return current_user

@router.get("/estatisticas", dependencies=[Depends(verificar_admin)])
async def obter_estatisticas_admin():
    """Retorna os dados reais do banco para o Dashboard do Administrador (Otimizado)."""
    db = get_database()
    
    # Validação de saúde do banco de dados (Fazemos primeiro para evitar consultas se estiver offline)
    if db is None:
        return {"usuariosAtivos": 0, "areasCadastradas": 0, "testesConfigurados": 0, "statusServidor": "Offline"}

    # 2. Executar TODAS as contagens simultaneamente (Paralelismo)
    resultados = await asyncio.gather(
        db.dim_usuario.count_documents({"is_ativo": True}),
        db.dim_area.count_documents({"is_ativo": True}),
        db.dim_indicador.count_documents({})
    )
    
    return {
        "usuariosAtivos": resultados[0],
        "areasCadastradas": resultados[1],
        "testesConfigurados": resultados[2],
        "statusServidor": "Online"
    }


@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_usuario_pelo_admin(usuario_in: UsuarioCreate):
    return await auth_service.criar_usuario(usuario_in)


@router.get("/usuarios", response_model=List[UsuarioResponse])
async def listar_usuarios(
    perfil: Optional[TipoPerfil] = Query(None),
    is_ativo: Optional[bool] = Query(None),
    db = Depends(get_database)
):
    filtro = {}
    if perfil: filtro["perfil"] = perfil
    if is_ativo is not None: filtro["is_ativo"] = is_ativo
    
    cursor = db.dim_usuario.find(filtro).sort("nome_completo", 1)
    usuarios = await cursor.to_list(length=100)
    # Converter ObjectId para string
    for u in usuarios: u["_id"] = str(u["_id"])
    return usuarios

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(usuario_id: str, obj_in: UsuarioUpdate, db = Depends(get_database)):
    from bson import ObjectId
    update_data = obj_in.model_dump(exclude_unset=True)
    
    resultado = await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, {"$set": update_data}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    usuario = await db.dim_usuario.find_one({"_id": ObjectId(usuario_id)})
    usuario["_id"] = str(usuario["_id"])
    return usuario

@router.patch("/usuarios/{usuario_id}/reset-password")
async def resetar_senha_usuario(usuario_id: str, db = Depends(get_database)):
    from bson import ObjectId
    # Gera uma senha aleatória de 8 caracteres
    nova_senha_temp = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    senha_hash = get_password_hash(nova_senha_temp)
    
    await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, {"$set": {
            "senha_hash": senha_hash,
            "precisa_trocar_senha": True
        }}
    )
    return {"nova_senha": nova_senha_temp}