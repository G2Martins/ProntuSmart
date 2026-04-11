from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
    perfil: str | None = None

class TrocarSenhaRequest(BaseModel):
    senha_temporaria: str
    nova_senha: str = Field(..., min_length=6)