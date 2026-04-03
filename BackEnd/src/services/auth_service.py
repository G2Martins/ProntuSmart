from fastapi import HTTPException
from src.core.database import get_database
from src.schemas.usuario import UsuarioCreate
from src.models.dim_usuario import DimUsuario
from src.core.security import get_password_hash

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
    
    # --- A MÁGICA DA CORREÇÃO AQUI ---
    # Converte o ObjectId nativo do Mongo para uma String comum antes de devolver para o FastAPI/Pydantic
    if usuario_criado and "_id" in usuario_criado:
        usuario_criado["_id"] = str(usuario_criado["_id"])
        
    return usuario_criado