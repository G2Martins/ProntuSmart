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
    # O form_data.username será preenchido com a matrícula no frontend
    user = await db.dim_usuario.find_one({"matricula": form_data.username})
    
    # Usando a função verify_password importada diretamente do core/security
    if not user or not verify_password(form_data.password, user["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Usando a função create_access_token importada diretamente do core/security
    access_token = create_access_token(
        data={"sub": user["matricula"], "perfil": user["perfil"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}