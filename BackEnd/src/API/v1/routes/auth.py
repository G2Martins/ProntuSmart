from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from bson import ObjectId

from src.core.config import settings
from src.core.database import get_database
from src.schemas.usuario import UsuarioCreate, UsuarioResponse
from src.schemas.auth import Token
from src.services import auth_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        matricula = payload.get("sub")
        if matricula is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    db = get_database()
    user = await db.dim_usuario.find_one({"matricula": matricula})
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(usuario_in: UsuarioCreate):
    return await auth_service.criar_usuario(usuario_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    # O form_data.username será preenchido com a matrícula no frontend
    user = await db.dim_usuario.find_one({"matricula": form_data.username})
    
    if not user or not auth_service.verify_password(form_data.password, user["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth_service.create_access_token(
        data={"sub": user["matricula"], "perfil": user["perfil"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}