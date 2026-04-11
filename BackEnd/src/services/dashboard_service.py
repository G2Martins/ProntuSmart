from datetime import datetime, timezone
from bson import ObjectId
from src.core.database import get_database


# ── helpers internos ────────────────────────────────────────────────────────

async def _nome_usuario(db, user_id: str) -> str:
    try:
        user = await db.dim_usuario.find_one({"_id": ObjectId(user_id)})
        return user.get("nome_completo", "Desconhecido") if user else "Desconhecido"
    except Exception:
        return "Desconhecido"


async def _nome_paciente(db, paciente_id: str) -> str:
    try:
        pac = await db.dim_paciente.find_one({"_id": ObjectId(paciente_id)})
        return pac.get("nome_completo", "Desconhecido") if pac else "Desconhecido"
    except Exception:
        return "Desconhecido"


# ── Epidemiologia ────────────────────────────────────────────────────────────

async def obter_epidemiologia() -> dict:
    db = get_database()

    # CIDs mais frequentes entre prontuários ativos
    pipeline_cids = [
        {"$match": {"status": "Ativo", "cid_id": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$cid_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 8},
    ]
    cids_agg = await db.fato_prontuario.aggregate(pipeline_cids).to_list(length=8)

    cids_mais_comuns = []
    for item in cids_agg:
        try:
            cid = await db.dim_cid.find_one({"_id": ObjectId(item["_id"])})
            if cid:
                cids_mais_comuns.append({
                    "codigo":   cid.get("codigo", ""),
                    "descricao": cid.get("descricao", ""),
                    "count":    item["count"],
                })
        except Exception:
            pass

    # Pacientes por área clínica
    pipeline_areas = [
        {"$match": {"status": "Ativo"}},
        {"$group": {"_id": "$area_atendimento", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    areas_agg = await db.fato_prontuario.aggregate(pipeline_areas).to_list(length=20)
    pacientes_por_area = [
        {"area": item["_id"] or "Sem área", "count": item["count"]}
        for item in areas_agg
    ]

    total_ativos = await db.fato_prontuario.count_documents({"status": "Ativo"})
    total_pacientes = await db.dim_paciente.count_documents({"is_ativo": True})

    return {
        "cids_mais_comuns":       cids_mais_comuns,
        "pacientes_por_area":     pacientes_por_area,
        "total_prontuarios_ativos": total_ativos,
        "total_pacientes":        total_pacientes,
    }


# ── Produtividade ────────────────────────────────────────────────────────────

async def obter_produtividade() -> dict:
    db = get_database()

    # Evoluções agrupadas por estagiário
    pipeline = [
        {"$group": {"_id": "$autor_id", "total_evolucoes": {"$sum": 1}}},
        {"$sort": {"total_evolucoes": -1}},
        {"$limit": 10},
    ]
    evs_agg = await db.fato_evolucao.aggregate(pipeline).to_list(length=10)

    evolucoes_por_estagiario = []
    for item in evs_agg:
        nome = await _nome_usuario(db, item["_id"])
        pront_ids = await db.fato_evolucao.distinct(
            "prontuario_id", {"autor_id": item["_id"]}
        )
        evolucoes_por_estagiario.append({
            "nome":             nome,
            "total_evolucoes":  item["total_evolucoes"],
            "total_prontuarios": len(pront_ids),
        })

    # Totais gerais de evoluções
    total      = await db.fato_evolucao.count_documents({})
    aprovadas  = await db.fato_evolucao.count_documents({"status": "Aprovado e Assinado"})
    pendentes  = await db.fato_evolucao.count_documents({"status": "Pendente de Revisão"})
    devolvidas = await db.fato_evolucao.count_documents({"status": "Ajustes Solicitados"})

    # Metas por status
    pipeline_metas = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    metas_agg = await db.fato_meta_smart.aggregate(pipeline_metas).to_list(length=20)
    metas_por_status = {item["_id"]: item["count"] for item in metas_agg}

    return {
        "evolucoes_por_estagiario": evolucoes_por_estagiario,
        "totais_evolucoes": {
            "total":     total,
            "aprovadas": aprovadas,
            "pendentes": pendentes,
            "devolvidas": devolvidas,
        },
        "metas_por_status": metas_por_status,
    }


# ── Alertas de Risco ─────────────────────────────────────────────────────────

async def obter_riscos() -> dict:
    db = get_database()
    alertas = []

    # 1. Pacientes com dor registrada na avaliação funcional
    pront_dor = await db.fato_prontuario.find(
        {"status": "Ativo", "dor": True}
    ).to_list(length=100)

    for p in pront_dor:
        nome = await _nome_paciente(db, p.get("paciente_id", ""))
        alertas.append({
            "prontuario_id": str(p["_id"]),
            "paciente_nome": nome,
            "area":          p.get("area_atendimento", ""),
            "motivo":        "Paciente com dor registrada na avaliação funcional",
            "tipo":          "dor",
            "prioridade":    "media",
        })

    # 2. Metas estagnadas: Em andamento ou Não iniciada,
    #    progresso < 30 % e data_limite já ultrapassada
    hoje = datetime.now(timezone.utc)
    metas_atrasadas = await db.fato_meta_smart.find({
        "status":               {"$in": ["Em andamento", "Não iniciada"]},
        "progresso_percentual": {"$lt": 30},
        "data_limite":          {"$lt": hoje},
    }).to_list(length=100)

    pronts_ja_incluidos: set[str] = set()
    for meta in metas_atrasadas:
        pront_id = meta.get("prontuario_id", "")
        if pront_id in pronts_ja_incluidos:
            continue
        try:
            pront = await db.fato_prontuario.find_one(
                {"_id": ObjectId(pront_id), "status": "Ativo"}
            )
            if pront:
                nome = await _nome_paciente(db, pront.get("paciente_id", ""))
                progresso = meta.get("progresso_percentual", 0)
                alertas.append({
                    "prontuario_id": str(pront["_id"]),
                    "paciente_nome": nome,
                    "area":          pront.get("area_atendimento", ""),
                    "motivo":        f"Meta atrasada com {progresso:.0f}% de progresso",
                    "tipo":          "meta_estagnada",
                    "prioridade":    "alta",
                })
                pronts_ja_incluidos.add(pront_id)
        except Exception:
            pass

    # Ordena: alta prioridade primeiro
    alertas.sort(key=lambda a: 0 if a["prioridade"] == "alta" else 1)

    return {
        "alertas":      alertas,
        "total_alertas": len(alertas),
        "por_tipo": {
            "dor":            sum(1 for a in alertas if a["tipo"] == "dor"),
            "meta_estagnada": sum(1 for a in alertas if a["tipo"] == "meta_estagnada"),
        },
    }
