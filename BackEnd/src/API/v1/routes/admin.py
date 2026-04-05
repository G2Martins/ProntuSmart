import secrets
import string
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId

from src.core.database import get_database
from src.core.security import get_current_user, get_password_hash
from src.models.dim_usuario import TipoPerfil, DimUsuario
from src.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter()

# Middleware para garantir que só Admins acedem a estas rotas
def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Funcionalidade exclusiva para Administradores."
        )
    return current_user

# 👇 NOVO MIDDLEWARE: Permite que Docentes também vejam a lista de usuários (necessário para a Triagem)
def verificar_admin_ou_docente(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") not in [TipoPerfil.ADMINISTRADOR, TipoPerfil.DOCENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Funcionalidade restrita."
        )
    return current_user


# ==========================================
# 1. ESTATÍSTICAS E SAÚDE DO SISTEMA
# ==========================================
@router.get("/estatisticas", dependencies=[Depends(verificar_admin)])
async def obter_estatisticas_admin(db = Depends(get_database)):
    """Retorna os dados reais do banco para o Dashboard do Administrador (Otimizado)."""
    if db is None:
        return {"statusServidor": "Offline"}

    try:
        # 1. Contagens ultrarrápidas usando count_documents (Resolve o travamento dos cards)
        total_usuarios = await db.dim_usuario.count_documents({})
        usuarios_ativos = await db.dim_usuario.count_documents({"is_ativo": True})
        
        areas_cadastradas = await db.dim_area.count_documents({"is_ativo": True})
        testes_configurados = await db.dim_indicador.count_documents({"is_ativo": True})
        
        total_cids = await db.dim_cid.count_documents({"is_ativo": True})
        total_pacientes = await db.dim_paciente.count_documents({"is_ativo": True})

        return {
            "usuariosAtivos": usuarios_ativos,
            "totalUsuarios": total_usuarios,
            "areasCadastradas": areas_cadastradas,
            "testesConfigurados": testes_configurados,
            "totalCids": total_cids,
            "totalPacientes": total_pacientes,
            "statusServidor": "Online",
            "saudeSistema": True
        }
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return {
            "usuariosAtivos": 0, "totalUsuarios": 0,
            "areasCadastradas": 0, "testesConfigurados": 0,
            "totalCids": 0, "totalPacientes": 0,
            "statusServidor": "Erro de Banco",
            "saudeSistema": False
        }


# ==========================================
# 2. GESTÃO DE USUÁRIOS (CRUD)
# ==========================================
@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_usuario(usuario_in: UsuarioCreate, db = Depends(get_database)):
    # Verifica duplicidade de Matrícula e E-mail
    if await db.dim_usuario.find_one({"matricula": usuario_in.matricula}):
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada no sistema.")
    if await db.dim_usuario.find_one({"email": usuario_in.email}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    # Gera a senha aleatória e o hash
    senha_plana = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    senha_hash = get_password_hash(senha_plana)
    
    dados_usuario = usuario_in.model_dump()
    dados_usuario["senha_hash"] = senha_hash
    dados_usuario["precisa_trocar_senha"] = True

    novo_usuario = DimUsuario(**dados_usuario)
    resultado = await db.dim_usuario.insert_one(novo_usuario.model_dump(by_alias=True, exclude_none=True))
    
    usuario_criado = await db.dim_usuario.find_one({"_id": resultado.inserted_id})
    usuario_criado["_id"] = str(usuario_criado["_id"])
    
    # Injeta a senha temporária APENAS na resposta de criação para o Admin ver (não é salva no banco assim)
    usuario_criado["senha_temporaria"] = senha_plana
    return usuario_criado

# 👇 ROTA ALTERADA PARA PERMITIR ADMIN E DOCENTE 👇
@router.get("/usuarios", response_model=List[UsuarioResponse], dependencies=[Depends(verificar_admin_ou_docente)])
async def listar_usuarios(
    perfil: Optional[TipoPerfil] = Query(None),
    is_ativo: Optional[bool] = Query(None),
    db = Depends(get_database)
):
    filtro = {}
    if perfil: filtro["perfil"] = perfil
    if is_ativo is not None: filtro["is_ativo"] = is_ativo
    
    cursor = db.dim_usuario.find(filtro).sort("nome_completo", 1)
    usuarios = await cursor.to_list(length=500)
    for u in usuarios: u["_id"] = str(u["_id"])
    return usuarios

@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse, dependencies=[Depends(verificar_admin)])
async def buscar_usuario(usuario_id: str, db = Depends(get_database)):
    usuario = await db.dim_usuario.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario["_id"] = str(usuario["_id"])
    return usuario

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse, dependencies=[Depends(verificar_admin)])
async def atualizar_usuario(usuario_id: str, obj_in: UsuarioUpdate, db = Depends(get_database)):
    update_data = obj_in.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado para atualização.")
        
    resultado = await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, {"$set": update_data}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    usuario = await db.dim_usuario.find_one({"_id": ObjectId(usuario_id)})
    usuario["_id"] = str(usuario["_id"])
    return usuario

@router.patch("/usuarios/{usuario_id}/reset-password", dependencies=[Depends(verificar_admin)])
async def resetar_senha_usuario(usuario_id: str, db = Depends(get_database)):
    # Gera uma senha aleatória provisória de 8 caracteres
    nova_senha_temp = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    senha_hash = get_password_hash(nova_senha_temp)
    
    # Atualiza a senha e ARMA A ARMADILHA obrigando a troca no próximo login!
    resultado = await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, 
        {"$set": {"senha_hash": senha_hash, "precisa_trocar_senha": True}}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return {"message": "Senha resetada com sucesso.", "nova_senha_temporaria": nova_senha_temp}

@router.patch("/usuarios/{usuario_id}/status", dependencies=[Depends(verificar_admin)])
async def alterar_status_usuario(usuario_id: str, is_ativo: bool = Query(...), db = Depends(get_database)):
    resultado = await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, {"$set": {"is_ativo": is_ativo}}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return {"message": f"Usuário {'ativado' if is_ativo else 'inativado'} com sucesso."}