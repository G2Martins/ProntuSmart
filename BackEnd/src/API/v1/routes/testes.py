"""Rotas para Testes/Escalas aplicadas ao paciente (Avaliação Funcional, Sunny, Mini-BEST)."""
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.core.database import get_database
from src.core.security import get_current_user
from src.models.dim_usuario import TipoPerfil
from src.models.fato_teste import FatoTeste, TipoTeste
from src.schemas.teste import TesteCreate, TesteResponse, TesteUpdate

router = APIRouter()


async def _verificar_acesso_prontuario(db, prontuario_id: str, current_user: dict) -> dict:
    pront = await db.fato_prontuario.find_one({"_id": ObjectId(prontuario_id)})
    if not pront:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")
    perfil = current_user.get("perfil")
    if perfil == TipoPerfil.ESTAGIARIO:
        user_id = str(current_user["_id"])
        area    = current_user.get("area_atendimento")
        if pront.get("estagiario_id") != user_id and pront.get("area_atendimento") != area:
            raise HTTPException(status_code=403, detail="Acesso negado a este prontuário.")
    return pront


async def _enriquecer(db, t: dict) -> dict:
    t["_id"] = str(t["_id"])
    try:
        u = await db.dim_usuario.find_one({"_id": ObjectId(t["aplicador_id"])})
        t["nome_aplicador"] = u.get("nome_completo") if u else None
    except Exception:
        t["nome_aplicador"] = None
    return t


@router.post("/", response_model=TesteResponse, status_code=status.HTTP_201_CREATED)
async def criar_teste(
    payload: TesteCreate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Aplica um teste a um prontuário. Apenas Estagiário pode registrar."""
    if current_user.get("perfil") != TipoPerfil.ESTAGIARIO:
        raise HTTPException(status_code=403, detail="Apenas Estagiários podem registrar testes.")

    pront = await _verificar_acesso_prontuario(db, payload.prontuario_id, current_user)

    teste = FatoTeste(
        prontuario_id    = payload.prontuario_id,
        paciente_id      = pront["paciente_id"],
        aplicador_id     = str(current_user["_id"]),
        tipo             = payload.tipo,
        dados            = payload.dados,
        pontuacao_total  = payload.pontuacao_total,
        pontuacao_maxima = payload.pontuacao_maxima,
        interpretacao    = payload.interpretacao,
        observacoes      = payload.observacoes,
    )
    res = await db.fato_teste.insert_one(teste.model_dump(by_alias=True, exclude_none=True))
    novo = await db.fato_teste.find_one({"_id": res.inserted_id})
    return await _enriquecer(db, novo)


@router.get("/prontuario/{prontuario_id}", response_model=List[TesteResponse])
async def listar_por_prontuario(
    prontuario_id: str,
    tipo: Optional[TipoTeste] = Query(None),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    await _verificar_acesso_prontuario(db, prontuario_id, current_user)
    filtro: dict = {"prontuario_id": prontuario_id}
    if tipo:
        filtro["tipo"] = tipo
    cursor = db.fato_teste.find(filtro).sort("data_aplicacao", -1)
    testes = await cursor.to_list(length=200)
    return [await _enriquecer(db, t) for t in testes]


@router.get("/{teste_id}", response_model=TesteResponse)
async def buscar_teste(
    teste_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    t = await db.fato_teste.find_one({"_id": ObjectId(teste_id)})
    if not t:
        raise HTTPException(status_code=404, detail="Teste não encontrado.")
    await _verificar_acesso_prontuario(db, t["prontuario_id"], current_user)
    return await _enriquecer(db, t)


@router.patch("/{teste_id}", response_model=TesteResponse)
async def atualizar_teste(
    teste_id: str,
    payload: TesteUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    t = await db.fato_teste.find_one({"_id": ObjectId(teste_id)})
    if not t:
        raise HTTPException(status_code=404, detail="Teste não encontrado.")

    perfil = current_user.get("perfil")
    if perfil == TipoPerfil.ESTAGIARIO and t.get("aplicador_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Apenas o autor pode editar este teste.")

    update = payload.model_dump(exclude_unset=True)
    if not update:
        raise HTTPException(status_code=400, detail="Nada para atualizar.")
    update["atualizado_em"] = datetime.now(timezone.utc)
    await db.fato_teste.update_one({"_id": ObjectId(teste_id)}, {"$set": update})
    novo = await db.fato_teste.find_one({"_id": ObjectId(teste_id)})
    return await _enriquecer(db, novo)


@router.delete("/{teste_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_teste(
    teste_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    t = await db.fato_teste.find_one({"_id": ObjectId(teste_id)})
    if not t:
        raise HTTPException(status_code=404, detail="Teste não encontrado.")
    perfil = current_user.get("perfil")
    if perfil == TipoPerfil.ESTAGIARIO and t.get("aplicador_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Apenas o autor pode excluir este teste.")
    await db.fato_teste.delete_one({"_id": ObjectId(teste_id)})
