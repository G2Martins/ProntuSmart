"""
Rotas de Relatórios Fisioterapêuticos.

RBAC:
- Administrador / Docente: lista todos os relatórios da clínica.
- Estagiário: lista apenas relatórios cujo paciente está vinculado a ele
              ou pertence à sua área de atuação.

Estados:
  Rascunho → (estagiário assina) → Aguardando Docente → (docente assina) → Finalizado
"""
import hashlib
import json
import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from bson import ObjectId
from io import BytesIO

from src.core.database import get_database
from src.core.security import get_current_user, verify_password
from src.models.dim_usuario import TipoPerfil
from src.models.fato_relatorio import (
    FatoRelatorio, TipoRelatorio, StatusRelatorio, Assinatura,
)
from src.schemas.relatorio import (
    RelatorioCreate, RelatorioUpdate, RelatorioAssinarRequest, RelatorioResponse,
)
from src.services.relatorio_pdf_service import gerar_pdf_padrao, gerar_pdf_completo

router = APIRouter()


# ════════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════════

def _hash_documento(payload: dict) -> str:
    """SHA256 do conteúdo serializado — garante imutabilidade."""
    base = {k: v for k, v in payload.items() if k not in ("assinatura_estagiario", "assinatura_docente", "_id", "criado_em", "atualizado_em")}
    raw  = json.dumps(base, default=str, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def _filtro_por_perfil(db, current_user: dict) -> dict:
    """Retorna um filtro Mongo que respeita as regras de acesso por perfil."""
    perfil = current_user.get("perfil")
    if perfil in (TipoPerfil.ADMINISTRADOR, TipoPerfil.DOCENTE):
        return {}

    # Estagiário: relatórios próprios OU de pacientes de sua área
    user_id = str(current_user["_id"])
    area    = current_user.get("area_atendimento")

    if not area:
        return {"estagiario_id": user_id}

    # Busca prontuários da área para liberar acesso
    cursor = db.fato_prontuario.find({"area_atendimento": area}, {"_id": 1})
    pront_ids = [str(p["_id"]) async for p in cursor]
    return {"$or": [
        {"estagiario_id":  user_id},
        {"prontuario_id":  {"$in": pront_ids}},
    ]}


async def _enriquecer(db, rel: dict) -> dict:
    """Adiciona nome_paciente, nome_estagiario, nome_docente, area, numero_prontuario."""
    rel["_id"] = str(rel["_id"])
    try:
        pac = await db.dim_paciente.find_one({"_id": ObjectId(rel["paciente_id"])})
        rel["nome_paciente"] = pac.get("nome_completo") if pac else None
    except Exception:
        rel["nome_paciente"] = None

    try:
        est = await db.dim_usuario.find_one({"_id": ObjectId(rel["estagiario_id"])})
        rel["nome_estagiario"] = est.get("nome_completo") if est else None
    except Exception:
        rel["nome_estagiario"] = None

    if rel.get("docente_id"):
        try:
            doc = await db.dim_usuario.find_one({"_id": ObjectId(rel["docente_id"])})
            rel["nome_docente"] = doc.get("nome_completo") if doc else None
        except Exception:
            rel["nome_docente"] = None
    else:
        rel["nome_docente"] = None

    try:
        pront = await db.fato_prontuario.find_one({"_id": ObjectId(rel["prontuario_id"])})
        if pront:
            rel["numero_prontuario"] = pront.get("numero_prontuario")
            rel["area_atendimento"]  = pront.get("area_atendimento")
    except Exception:
        pass

    return rel


async def _prontuario_acessivel(db, prontuario_id: str, current_user: dict) -> dict:
    """Carrega prontuário verificando se o usuário pode acessá-lo."""
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


# ════════════════════════════════════════════════════════════════
#  Endpoints
# ════════════════════════════════════════════════════════════════

@router.post("/", response_model=RelatorioResponse, status_code=status.HTTP_201_CREATED)
async def criar_relatorio(
    payload: RelatorioCreate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """
    Cria um rascunho de relatório a partir de um prontuário.
    Apenas Estagiário e Docente podem solicitar.
    """
    if current_user.get("perfil") not in (TipoPerfil.ESTAGIARIO, TipoPerfil.DOCENTE, TipoPerfil.ADMINISTRADOR):
        raise HTTPException(status_code=403, detail="Acesso negado.")

    pront = await _prontuario_acessivel(db, payload.prontuario_id, current_user)

    # Numeração sequencial
    ano = datetime.now().year
    seq = random.randint(10000, 99999)
    numero = f"REL-{ano}-{seq:05d}"

    relatorio = FatoRelatorio(
        prontuario_id  = payload.prontuario_id,
        paciente_id    = pront["paciente_id"],
        estagiario_id  = pront["estagiario_id"],  # vínculo formal: o estagiário do prontuário
        docente_id     = pront.get("docente_id"),
        numero_relatorio = numero,
        tipo   = payload.tipo,
        status = StatusRelatorio.RASCUNHO,
        diagnostico_clinico          = payload.diagnostico_clinico,
        queixa_principal             = payload.queixa_principal,
        diagnostico_fisioterapeutico = payload.diagnostico_fisioterapeutico,
        objetivos_tratamento         = payload.objetivos_tratamento,
        atividades_realizadas        = payload.atividades_realizadas,
        observacoes_evolucao         = payload.observacoes_evolucao,
        consideracoes_finais         = payload.consideracoes_finais,
    )

    res = await db.fato_relatorio.insert_one(
        relatorio.model_dump(by_alias=True, exclude_none=True)
    )
    novo = await db.fato_relatorio.find_one({"_id": res.inserted_id})
    return await _enriquecer(db, novo)


@router.get("/meus", response_model=List[RelatorioResponse])
async def listar_meus_relatorios(
    tipo: Optional[TipoRelatorio] = Query(None),
    status_filter: Optional[StatusRelatorio] = Query(None, alias="status"),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """
    Lista relatórios respeitando RBAC.
    Admin/Docente: todos. Estagiário: próprios + da sua área.
    Ordenação: mais recentes primeiro.
    """
    filtro = await _filtro_por_perfil(db, current_user)
    if tipo:
        filtro["tipo"] = tipo
    if status_filter:
        filtro["status"] = status_filter

    cursor = db.fato_relatorio.find(filtro).sort("criado_em", -1)
    relatorios = await cursor.to_list(length=500)
    return [await _enriquecer(db, r) for r in relatorios]


@router.get("/{relatorio_id}", response_model=RelatorioResponse)
async def buscar_relatorio(
    relatorio_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    rel = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    if not rel:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    # Verificação de acesso
    filtro = await _filtro_por_perfil(db, current_user)
    if filtro:
        # Re-busca aplicando filtro garante que respeita RBAC
        rel_check = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id), **filtro})
        if not rel_check:
            raise HTTPException(status_code=403, detail="Acesso negado a este relatório.")

    return await _enriquecer(db, rel)


@router.patch("/{relatorio_id}", response_model=RelatorioResponse)
async def atualizar_relatorio(
    relatorio_id: str,
    payload: RelatorioUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Edita conteúdo de um rascunho. Bloqueado após qualquer assinatura."""
    rel = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    if not rel:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    if rel.get("status") != StatusRelatorio.RASCUNHO:
        raise HTTPException(status_code=400, detail="Relatório já assinado — não é mais editável.")

    user_id = str(current_user["_id"])
    perfil  = current_user.get("perfil")
    if perfil == TipoPerfil.ESTAGIARIO and rel.get("estagiario_id") != user_id:
        raise HTTPException(status_code=403, detail="Apenas o estagiário responsável pode editar.")

    update_data = payload.model_dump(exclude_unset=True)
    update_data["atualizado_em"] = datetime.now(timezone.utc)

    await db.fato_relatorio.update_one(
        {"_id": ObjectId(relatorio_id)}, {"$set": update_data}
    )
    atualizado = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    return await _enriquecer(db, atualizado)


@router.post("/{relatorio_id}/assinar", response_model=RelatorioResponse)
async def assinar_relatorio(
    relatorio_id: str,
    payload: RelatorioAssinarRequest,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """
    Assinatura digital — exige reentrada da senha.
    Fluxo:
      Estagiário assina → status vira "Aguardando Docente"
      Docente assina    → status vira "Finalizado"
    """
    rel = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    if not rel:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    # Confirmação de identidade
    if not verify_password(payload.senha, current_user.get("senha_hash", "")):
        raise HTTPException(status_code=401, detail="Senha incorreta. Assinatura não registrada.")

    perfil  = current_user.get("perfil")
    user_id = str(current_user["_id"])

    assinatura = Assinatura(
        usuario_id     = user_id,
        nome_completo  = current_user.get("nome_completo", "—"),
        matricula      = current_user.get("matricula", "—"),
        perfil         = str(perfil),
        data_assinatura = datetime.now(timezone.utc),
        hash_documento  = _hash_documento(rel),
    )

    update_data: dict = {"atualizado_em": datetime.now(timezone.utc)}

    if perfil == TipoPerfil.ESTAGIARIO:
        if rel.get("estagiario_id") != user_id:
            raise HTTPException(status_code=403, detail="Apenas o estagiário responsável pode assinar como autor.")
        if rel.get("assinatura_estagiario"):
            raise HTTPException(status_code=400, detail="Você já assinou este relatório.")
        if rel.get("status") != StatusRelatorio.RASCUNHO:
            raise HTTPException(status_code=400, detail="Relatório não está em rascunho.")
        update_data["assinatura_estagiario"] = assinatura.model_dump()
        update_data["status"] = StatusRelatorio.AGUARDANDO_DOCENTE

    elif perfil in (TipoPerfil.DOCENTE, TipoPerfil.ADMINISTRADOR):
        if not rel.get("assinatura_estagiario"):
            raise HTTPException(status_code=400, detail="O estagiário precisa assinar primeiro.")
        if rel.get("assinatura_docente"):
            raise HTTPException(status_code=400, detail="Este relatório já foi assinado pelo docente.")
        update_data["assinatura_docente"] = assinatura.model_dump()
        update_data["status"]       = StatusRelatorio.FINALIZADO
        update_data["data_emissao"] = datetime.now(timezone.utc)
        update_data["docente_id"]   = user_id  # registra o docente que assinou
        update_data["hash_integridade"] = _hash_documento(rel)
    else:
        raise HTTPException(status_code=403, detail="Perfil sem permissão para assinar.")

    await db.fato_relatorio.update_one({"_id": ObjectId(relatorio_id)}, {"$set": update_data})
    atualizado = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    return await _enriquecer(db, atualizado)


@router.delete("/{relatorio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_relatorio(
    relatorio_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Cancela um rascunho (apenas o autor estagiário ou admin)."""
    rel = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    if not rel:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    if rel.get("status") == StatusRelatorio.FINALIZADO:
        raise HTTPException(status_code=400, detail="Relatórios finalizados não podem ser excluídos.")

    user_id = str(current_user["_id"])
    perfil  = current_user.get("perfil")
    if perfil == TipoPerfil.ESTAGIARIO and rel.get("estagiario_id") != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    await db.fato_relatorio.delete_one({"_id": ObjectId(relatorio_id)})


@router.get("/{relatorio_id}/pdf")
async def baixar_pdf(
    relatorio_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Gera e devolve o PDF do relatório (padrão ou completo)."""
    rel = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id)})
    if not rel:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    # RBAC
    filtro = await _filtro_por_perfil(db, current_user)
    if filtro:
        rel_check = await db.fato_relatorio.find_one({"_id": ObjectId(relatorio_id), **filtro})
        if not rel_check:
            raise HTTPException(status_code=403, detail="Acesso negado a este relatório.")

    rel["_id"] = str(rel["_id"])

    paciente   = await db.dim_paciente.find_one({"_id": ObjectId(rel["paciente_id"])}) or {}
    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(rel["prontuario_id"])}) or {}

    if rel.get("tipo") == TipoRelatorio.COMPLETO:
        evolucoes_cursor = db.fato_evolucao.find({"prontuario_id": rel["prontuario_id"]}).sort("criado_em", 1)
        evolucoes = await evolucoes_cursor.to_list(length=500)
        metas_cursor = db.fato_meta_smart.find({"prontuario_id": rel["prontuario_id"]}).sort("criado_em", 1)
        metas = await metas_cursor.to_list(length=500)
        pdf_bytes = gerar_pdf_completo(rel, paciente, prontuario, evolucoes, metas)
        filename  = f"{rel['numero_relatorio']}_completo.pdf"
    else:
        pdf_bytes = gerar_pdf_padrao(rel, paciente, prontuario)
        filename  = f"{rel['numero_relatorio']}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
