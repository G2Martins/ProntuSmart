from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException, status
from src.core.config import settings
from src.core.database import get_database
from src.schemas.usuario import UsuarioCreate
from src.models.dim_usuario import DimUsuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def criar_usuario(usuario_in: UsuarioCreate) -> dict:
    db = get_database()
    
    # Verifica se a matrícula já existe
    usuario_existente = await db.dim_usuario.find_one({"matricula": usuario_in.matricula})
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada no sistema.")
    
    usuario_dict = usuario_in.model_dump(exclude={"senha"})
    usuario_dict["senha_hash"] = get_password_hash(usuario_in.senha)
    
    novo_usuario = DimUsuario(**usuario_dict)
    resultado = await db.dim_usuario.insert_one(novo_usuario.model_dump(by_alias=True, exclude_none=True))
    
    usuario_criado = await db.dim_usuario.find_one({"_id": resultado.inserted_id})
    return usuario_criado