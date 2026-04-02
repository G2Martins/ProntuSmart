from fastapi import APIRouter, Depends, HTTPException, status
from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.schemas.usuario import UsuarioCreate, UsuarioResponse
from src.services import auth_service

router = APIRouter()

# Dependência de Segurança: Verifica se o utilizador logado é realmente Administrador
def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Funcionalidade exclusiva para Administradores."
        )
    return current_user

@router.get("/estatisticas", dependencies=[Depends(verificar_admin)])
async def obter_estatisticas_admin():
    """Retorna os dados reais do banco para o Dashboard do Administrador."""
    db = get_database()
    
    # Contagens reais no MongoDB
    usuarios_ativos = await db.dim_usuario.count_documents({"is_ativo": True})
    areas_cadastradas = await db.dim_area.count_documents({"is_ativo": True})
    testes_configurados = await db.dim_indicador.count_documents({})
    
    # Validação de saúde do banco de dados
    status_db = "Online" if db is not None else "Offline"

    return {
        "usuariosAtivos": usuarios_ativos,
        "areasCadastradas": areas_cadastradas,
        "testesConfigurados": testes_configurados,
        "statusServidor": status_db
    }

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_usuario_pelo_admin(usuario_in: UsuarioCreate):
    """Permite ao Administrador criar Estagiários, Docentes ou outros Admins."""
    return await auth_service.criar_usuario(usuario_in)