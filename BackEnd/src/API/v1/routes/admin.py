from fastapi import APIRouter, Depends, HTTPException, status
from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.schemas.usuario import UsuarioCreate, UsuarioResponse
from src.services import auth_service
import asyncio 

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

# ... (Mantenha a rota de @router.post("/usuarios") exatamente como estava abaixo)
@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_usuario_pelo_admin(usuario_in: UsuarioCreate):
    return await auth_service.criar_usuario(usuario_in)