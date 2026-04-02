from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.database import connect_to_mongo, close_mongo_connection
from src.API.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa ao iniciar
    await connect_to_mongo()
    yield
    # Executa ao desligar
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configuração CORS para permitir acesso do Frontend Angular
# 2. Configuração do CORS para permitir o Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], # Permite apenas o seu frontend local
    allow_credentials=True,
    allow_methods=["*"], # Permite POST, GET, PUT, PATCH, DELETE
    allow_headers=["*"], # Permite todos os cabeçalhos (inclusive o Authorization)
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Bem-vindo à API do ProntuSMART!"}