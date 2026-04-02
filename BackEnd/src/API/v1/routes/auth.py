import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.database import get_database
from src.schemas.usuario import UsuarioCreate, UsuarioResponse
from src.schemas.auth import Token
from src.services import auth_service
from src.core.security import get_current_user, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(usuario_in: UsuarioCreate):
    return await auth_service.criar_usuario(usuario_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    
    # 1. Busca o usuário no banco de dados
    user = await db.dim_usuario.find_one({"matricula": form_data.username})
    
    # 2. Verifica se o usuário existe ANTES de fazer qualquer outra coisa
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Validação de senha sem travar o servidor (A Mágica!)
    # Usamos o user.get() para evitar KeyError (Erro 500) caso o campo não exista.
    # Usamos asyncio.to_thread para rodar o bcrypt pesado em segundo plano, liberando o FastAPI.
    senha_valida = await asyncio.to_thread(
        verify_password, 
        form_data.password, 
        user.get("senha_hash", "")
    )
    
    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. Gera o Token JWT
    access_token = create_access_token(
        data={"sub": user["matricula"], "perfil": user.get("perfil")}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}