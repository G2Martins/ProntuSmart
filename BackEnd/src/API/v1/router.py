from fastapi import APIRouter

from src.API.v1.routes import (
    auth,
    pacientes,
    prontuarios,
    metas_smart,
    evolucoes,
    medicoes,
    admin
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(pacientes.router, prefix="/pacientes", tags=["Pacientes"])
api_router.include_router(prontuarios.router, prefix="/prontuarios", tags=["Prontuários"])
api_router.include_router(metas_smart.router, prefix="/metas-smart", tags=["Metas SMART"])
api_router.include_router(evolucoes.router, prefix="/evolucoes", tags=["Evoluções"])
api_router.include_router(medicoes.router, prefix="/medicoes", tags=["Medições"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administração"])