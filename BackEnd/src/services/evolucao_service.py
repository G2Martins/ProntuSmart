from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from src.core.database import get_database
from src.schemas.evolucao import EvolucaoCreate
from src.models.fato_evolucao import FatoEvolucao, MedicaoItem
from src.utils.helpers import calcular_progresso
from src.models.dim_status import StatusMeta, ProgressoMeta, CondicaoMeta  # ← adicionar os dois enums

async def registrar_evolucao(evolucao_in: EvolucaoCreate, autor_id: str) -> dict:
    db = get_database()

    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(evolucao_in.prontuario_id)})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")

    medicoes_modelo = [
        MedicaoItem(
            indicador_id=m.indicador_id,
            nome_indicador=m.nome_indicador,
            valor_registrado=m.valor_registrado,
            unidade=m.unidade
        ) for m in evolucao_in.medicoes
    ]

    # ── Converte str → Enum com segurança ──────────────────
    houve_progresso_enum: ProgressoMeta | None = None
    if evolucao_in.houve_progresso:
        try:
            houve_progresso_enum = ProgressoMeta(evolucao_in.houve_progresso)
        except ValueError:
            pass  # valor inválido ignorado silenciosamente

    condicao_meta_enum: CondicaoMeta | None = None
    if evolucao_in.condicao_meta:
        try:
            condicao_meta_enum = CondicaoMeta(evolucao_in.condicao_meta)
        except ValueError:
            pass

    nova_evolucao = FatoEvolucao(
        prontuario_id=evolucao_in.prontuario_id,
        autor_id=autor_id,
        texto_clinico=evolucao_in.texto_clinico,
        medicoes=medicoes_modelo,
        houve_progresso=houve_progresso_enum,      # ← enum ou None
        condicao_meta=condicao_meta_enum,          # ← enum ou None
        motivo_ajuste=evolucao_in.motivo_ajuste,
        proxima_revisao=evolucao_in.proxima_revisao,
        indicador_reavaliado=evolucao_in.indicador_reavaliado,
        valor_atual=evolucao_in.valor_atual,
    )

    resultado = await db.fato_evolucao.insert_one(
        nova_evolucao.model_dump(by_alias=True, exclude_none=True)
    )

    await db.fato_prontuario.update_one(
        {"_id": ObjectId(evolucao_in.prontuario_id)},
        {
            "$inc": {"total_sessoes": 1},
            "$set": {"data_ultima_evolucao": datetime.now(timezone.utc)}
        }
    )

    # ── Recalcula progresso da meta vinculada ───────────────
    if evolucao_in.meta_id_reavaliada and evolucao_in.valor_atual:
        try:
            valor_numerico = float(evolucao_in.valor_atual)
            meta = await db.fato_meta_smart.find_one({"_id": ObjectId(evolucao_in.meta_id_reavaliada)})
            if meta:
                indicador = await db.dim_indicador.find_one({"_id": ObjectId(meta["indicador_id"])})
                if indicador:
                    novo_progresso = calcular_progresso(
                        valor_inicial=float(meta["valor_inicial"]),
                        valor_alvo=float(meta["valor_alvo"]),
                        valor_atual=valor_numerico,
                        direcao=indicador["direcao_melhora"]
                    )
                    novo_status = StatusMeta.CONCLUIDA if novo_progresso >= 100.0 else StatusMeta.EM_ANDAMENTO
                    await db.fato_meta_smart.update_one(
                        {"_id": ObjectId(evolucao_in.meta_id_reavaliada)},
                        {"$set": {
                            "progresso_percentual": novo_progresso,
                            "status": novo_status,
                            "atualizado_em": datetime.now(timezone.utc)
                        }}
                    )
        except (ValueError, TypeError):
            pass

    criado = await db.fato_evolucao.find_one({"_id": resultado.inserted_id})
    criado["_id"] = str(criado["_id"])
    return criado

async def listar_por_prontuario(prontuario_id: str) -> list:
    db = get_database()
    cursor = db.fato_evolucao.find({"prontuario_id": prontuario_id}).sort("criado_em", -1)
    evolucoes = await cursor.to_list(length=200)
    for e in evolucoes:
        e["_id"] = str(e["_id"])
    return evolucoes

async def contar_pendentes_por_docente(docente_id: str) -> int:
    db = get_database()
    return await db.fato_evolucao.count_documents({"status": "Pendente de Revisão"})

async def listar_pendentes_por_docente(docente_id: str) -> list:
    db = get_database()
    cursor = db.fato_evolucao.find({"status": "Pendente de Revisão"}).sort("criado_em", 1)
    pendentes = await cursor.to_list(length=200)
    for e in pendentes:
        e["_id"] = str(e["_id"])
    return pendentes

async def revisar_evolucao(evolucao_id: str, docente_id: str, acao: str, feedback: str | None) -> dict:
    db = get_database()
    evolucao = await db.fato_evolucao.find_one({"_id": ObjectId(evolucao_id)})
    if not evolucao:
        raise HTTPException(status_code=404, detail="Evolução não encontrada.")
    if evolucao.get("status") != "Pendente de Revisão":
        raise HTTPException(status_code=400, detail="Esta evolução já foi revisada.")
    prontuario = await db.fato_prontuario.find_one({"_id": ObjectId(evolucao["prontuario_id"])})
    if not prontuario:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado.")
    if acao == "aprovar":
        novo_status = "Aprovado e Assinado"
    elif acao == "devolver":
        if not feedback:
            raise HTTPException(status_code=400, detail="Feedback obrigatório ao devolver.")
        novo_status = "Ajustes Solicitados"
    else:
        raise HTTPException(status_code=400, detail="Ação inválida.")
    await db.fato_evolucao.update_one(
        {"_id": ObjectId(evolucao_id)},
        {"$set": {
            "status": novo_status,
            "docente_revisor_id": docente_id,
            "feedback_docente": feedback,
            "atualizado_em": datetime.now(timezone.utc)
        }}
    )
    atualizada = await db.fato_evolucao.find_one({"_id": ObjectId(evolucao_id)})
    atualizada["_id"] = str(atualizada["_id"])
    return atualizada