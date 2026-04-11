from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.core.database import get_database

# Configuração do OAuth2 para o FastAPI saber onde o frontend vai bater para pegar o token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_password_hash(password: str) -> str:
    """Gera o hash da senha em texto plano usando bcrypt diretamente."""
    salt = bcrypt.gensalt()
    # O bcrypt exige bytes, por isso usamos o encode('utf-8')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano bate com o hash salvo no banco."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except ValueError:
        # Se houver algum problema de formatação no hash antigo, retorna False por segurança
        return False

"""Gera o token JWT de acesso com tempo de expiração."""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # A CORREÇÃO ESTÁ AQUI: Usar sempre datetime.now(timezone.utc)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Por padrão, vamos colocar 60 minutos de duração se não for informado
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

"""
    Dependência (Depends) injetada nas rotas protegidas.
    Verifica o token JWT e retorna o usuário logado do banco de dados.
    Se o token for inválido ou o usuário não existir, lança uma HTTPException 401."""
async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_database)):
    from bson import ObjectId # Importar aqui para garantir conversão
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Se o token estiver expirado, ele cai direto no except JWTError abaixo!
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Procura no MongoDB pelo _id convertido
    user = await db.dim_usuario.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
        
    return user