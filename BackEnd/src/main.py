import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.database import connect_to_mongo, close_mongo_connection
from src.core.monitor import monitor
from src.API.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def coletar_metricas(request: Request, call_next):
    inicio = time.perf_counter()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        dur_ms = (time.perf_counter() - inicio) * 1000
        monitor.registrar_request(
            metodo=request.method,
            path=request.url.path,
            status=500,
            dur_ms=dur_ms,
        )
        raise
    dur_ms = (time.perf_counter() - inicio) * 1000
    # Ignora preflight CORS para não poluir métricas
    if request.method != "OPTIONS":
        monitor.registrar_request(
            metodo=request.method,
            path=request.url.path,
            status=status_code,
            dur_ms=dur_ms,
        )
        # Tracking de logins (auth/login)
        if request.url.path.endswith("/auth/login") and request.method == "POST":
            monitor.registrar_login(sucesso=(status_code == 200))
    return response


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Bem-vindo à API do ProntuSMART!"}
