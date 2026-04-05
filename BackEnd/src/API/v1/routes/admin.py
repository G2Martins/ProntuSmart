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


# ==========================================
# 1. ESTATÍSTICAS E SAÚDE DO SISTEMA
# ==========================================
@router.get("/estatisticas", dependencies=[Depends(verificar_admin)])
async def obter_estatisticas_admin(db = Depends(get_database)):
    """Retorna os dados reais do banco para o Dashboard do Administrador (Otimizado)."""
    if db is None:
        return {"statusServidor": "Offline"}

    try:
        # 1. Contagens ultrarrápidas usando count_documents (Resolve o travamento dos 1000+)
        # O MongoDB apenas conta os índices, sem baixar os documentos para a RAM
        total_usuarios = await db.dim_usuario.count_documents({})
        usuarios_ativos = await db.dim_usuario.count_documents({"is_ativo": True})
        total_areas = await db.dim_area.count_documents({})
        total_indicadores = await db.dim_indicador.count_documents({})
        total_cids = await db.dim_cid.count_documents({})
        
        # Prevenção caso as coleções de pacientes e prontuários ainda não existam
        total_pacientes = await db.dim_paciente.count_documents({}) if "dim_paciente" in await db.list_collection_names() else 0
        total_prontuarios = await db.fato_prontuario.count_documents({}) if "fato_prontuario" in await db.list_collection_names() else 0

        # 2. Metadados de Saúde do MongoDB (Tamanho, Coleções, etc)
        db_stats = await db.command("dbstats")
        
        # O tamanho dos dados (dataSize) vem em bytes. Vamos converter para Megabytes (MB)
        tamanho_mb = round(db_stats.get("dataSize", 0) / (1024 * 1024), 2)

        return {
            "statusServidor": "Online",
            
            # Métricas do Sistema Clínico
            "usuariosAtivos": usuarios_ativos,
            "totalUsuarios": total_usuarios,
            "areasCadastradas": total_areas,
            "testesConfigurados": total_indicadores,
            "totalCids": total_cids,
            "totalPacientes": total_pacientes,
            "totalProntuarios": total_prontuarios,
            
            # Métricas de Saúde do Servidor (Para o novo Dashboard Técnico)
            "saudeSistema": {
                "bancoDados": "MongoDB",
                "tamanhoDadosMB": tamanho_mb,
                "totalColecoes": db_stats.get("collections", 0),
                "totalDocumentosGerais": db_stats.get("objects", 0)
            }
        }
    except Exception as e:
        return {"statusServidor": "Erro", "detalhe": str(e)}

# ==========================================
# 2. GESTÃO DE USUÁRIOS (CRUD COMPLETO)
# ==========================================
@router.get("/usuarios", response_model=List[UsuarioResponse], dependencies=[Depends(verificar_admin)])
async def listar_usuarios(
    perfil: Optional[TipoPerfil] = Query(None),
    is_ativo: Optional[bool] = Query(None),
    db = Depends(get_database)
):
    filtro = {}
    if perfil: filtro["perfil"] = perfil
    if is_ativo is not None: filtro["is_ativo"] = is_ativo
    
    cursor = db.dim_usuario.find(filtro).sort("nome_completo", 1)
    
    # Aqui mantemos o limite no to_list para proteger a API caso tentem listar 10.000 usuários na tela de uma vez
    usuarios = await cursor.to_list(length=500)
    for u in usuarios: u["_id"] = str(u["_id"])
    return usuarios

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_usuario(usuario_in: UsuarioCreate, db = Depends(get_database)):
    # Verifica se a matrícula ou email já existem
    if await db.dim_usuario.find_one({"matricula": usuario_in.matricula}):
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada.")
    if await db.dim_usuario.find_one({"email": usuario_in.email}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    # Cria o Hash da senha
    senha_hasheada = get_password_hash(usuario_in.senha)
    
    # Monta o dicionário mesclando os dados com a senha hasheada (remove a senha em texto plano)
    dados_db = usuario_in.model_dump(exclude={"senha"})
    dados_db["senha_hash"] = senha_hasheada
    
    novo_usuario = DimUsuario(**dados_db)
    resultado = await db.dim_usuario.insert_one(novo_usuario.model_dump(by_alias=True, exclude_none=True))
    
    usuario_criado = await db.dim_usuario.find_one({"_id": resultado.inserted_id})
    usuario_criado["_id"] = str(usuario_criado["_id"])
    return usuario_criado

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
        {"$set": {
            "senha_hash": senha_hash,
            "precisa_trocar_senha": True
        }}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return {"nova_senha": nova_senha_temp}