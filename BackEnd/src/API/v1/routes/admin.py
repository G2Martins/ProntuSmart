import platform
import secrets
import string
import sys
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId

from src.core.database import get_database
from src.core.monitor import monitor
from src.core.security import get_current_user, get_password_hash
from src.models.dim_solicitacao import StatusSolicitacao
from src.models.dim_usuario import TipoPerfil, DimUsuario
from src.schemas.solicitacao import (
    SolicitacaoAprovar, SolicitacaoRecusar, SolicitacaoResponse,
)
from src.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter()

# Middleware para garantir que só Admins acedem a estas rotas
def verificar_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("perfil") != TipoPerfil.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Funcionalidade exclusiva para Administradores."
        )
    return current_user


# ==========================================
# 1. ESTATÍSTICAS E SAÚDE DO SISTEMA
# ==========================================
@router.get("/estatisticas", dependencies=[Depends(verificar_admin)])
async def obter_estatisticas_admin(db = Depends(get_database)):
    """Retorna os dados reais do banco para o Dashboard do Administrador (Otimizado)."""
    if db is None:
        return {"statusServidor": "Offline"}

    try:
        # 1. Contagens ultrarrápidas usando count_documents (Resolve o travamento dos 1000+)
        # O MongoDB apenas conta os índices, sem baixar os documentos para a RAM
        total_usuarios = await db.dim_usuario.count_documents({})
        usuarios_ativos = await db.dim_usuario.count_documents({"is_ativo": True})
        total_areas = await db.dim_area.count_documents({})
        total_indicadores = await db.dim_indicador.count_documents({})
        total_cids = await db.dim_cid.count_documents({})
        
        # Prevenção caso as coleções de pacientes e prontuários ainda não existam
        total_pacientes = await db.dim_paciente.count_documents({}) if "dim_paciente" in await db.list_collection_names() else 0
        total_prontuarios = await db.fato_prontuario.count_documents({}) if "fato_prontuario" in await db.list_collection_names() else 0

        # 2. Metadados de Saúde do MongoDB (Tamanho, Coleções, etc)
        db_stats = await db.command("dbstats")
        
        # O tamanho dos dados (dataSize) vem em bytes. Vamos converter para Megabytes (MB)
        tamanho_mb = round(db_stats.get("dataSize", 0) / (1024 * 1024), 2)

        return {
            "statusServidor": "Online",
            
            # Métricas do Sistema Clínico
            "usuariosAtivos": usuarios_ativos,
            "totalUsuarios": total_usuarios,
            "areasCadastradas": total_areas,
            "testesConfigurados": total_indicadores,
            "totalCids": total_cids,
            "totalPacientes": total_pacientes,
            "totalProntuarios": total_prontuarios,
            
            # Métricas de Saúde do Servidor (Para o novo Dashboard Técnico)
            "saudeSistema": {
                "bancoDados": "MongoDB",
                "tamanhoDadosMB": tamanho_mb,
                "totalColecoes": db_stats.get("collections", 0),
                "totalDocumentosGerais": db_stats.get("objects", 0)
            }
        }
    except Exception as e:
        return {"statusServidor": "Erro", "detalhe": str(e)}

# ==========================================
# 1.2. MONITORAMENTO PROFUNDO DO SISTEMA
# ==========================================
@router.get("/monitoramento", dependencies=[Depends(verificar_admin)])
async def monitoramento_completo(db = Depends(get_database)):
    """Snapshot detalhado do sistema — métricas reais (DB + runtime + ambiente)."""
    resultado: dict = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
    }

    # ── Runtime ──────────────────────────────────────────────
    uptime_seg = monitor.uptime_segundos()
    resultado["runtime"] = {
        "iniciado_em":      monitor.iniciado_iso,
        "uptime_segundos":  uptime_seg,
        "uptime_humano":    _formatar_uptime(uptime_seg),
        "python_versao":    sys.version.split()[0],
        "implementacao":    platform.python_implementation(),
        "plataforma":       f"{platform.system()} {platform.release()}",
        "arquitetura":      platform.machine(),
    }

    # ── Tráfego HTTP ─────────────────────────────────────────
    resultado["trafego"] = {
        "total_requisicoes":  monitor.total_requests,
        "por_status":         monitor.por_status,
        "por_metodo":         monitor.por_metodo,
        "media_ms":           round(monitor.media_ms(), 2),
        "p95_ms":             round(monitor.percentil(0.95), 2),
        "p99_ms":             round(monitor.percentil(0.99), 2),
        "rps":                round(monitor.total_requests / uptime_seg, 3) if uptime_seg > 0 else 0,
        "top_endpoints":      monitor.top_endpoints(8),
        "endpoints_lentos":   monitor.slow_endpoints(5),
        "ultimas_requisicoes": list(monitor.recent_requests)[-15:],
        "ultimos_erros":       list(monitor.recent_errors)[-10:],
    }

    # ── Autenticação ────────────────────────────────────────
    total_logins = monitor.logins_sucesso + monitor.logins_falha
    taxa_sucesso = (monitor.logins_sucesso / total_logins * 100) if total_logins else 100.0
    resultado["autenticacao"] = {
        "logins_sucesso":  monitor.logins_sucesso,
        "logins_falha":    monitor.logins_falha,
        "taxa_sucesso_%":  round(taxa_sucesso, 1),
    }

    # ── Banco de Dados ───────────────────────────────────────
    if db is None:
        resultado["banco"] = {"status": "Offline"}
        return resultado

    try:
        db_stats = await db.command("dbstats")
        server   = await db.command("serverStatus")

        # Métricas por coleção
        nomes = await db.list_collection_names()
        colecoes = []
        for nome in sorted(nomes):
            try:
                stats = await db.command("collStats", nome)
                colecoes.append({
                    "nome":       nome,
                    "documentos": stats.get("count", 0),
                    "tamanho_kb": round(stats.get("size", 0) / 1024, 1),
                    "indices":    stats.get("nindexes", 0),
                    "indice_kb":  round(stats.get("totalIndexSize", 0) / 1024, 1),
                })
            except Exception:
                continue

        connections = server.get("connections", {}) or {}
        opcounters  = server.get("opcounters",  {}) or {}
        mem         = server.get("mem",         {}) or {}
        network     = server.get("network",     {}) or {}

        resultado["banco"] = {
            "status":           "Online",
            "motor":            "MongoDB",
            "versao":           server.get("version", "—"),
            "host":             server.get("host", "—"),
            "uptime_segundos":  int(server.get("uptime", 0)),
            "uptime_humano":    _formatar_uptime(int(server.get("uptime", 0))),
            "data_size_mb":     round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
            "storage_size_mb":  round(db_stats.get("storageSize", 0) / (1024 * 1024), 2),
            "index_size_mb":    round(db_stats.get("indexSize", 0) / (1024 * 1024), 2),
            "total_colecoes":   db_stats.get("collections", 0),
            "total_documentos": db_stats.get("objects", 0),
            "total_indices":    db_stats.get("indexes", 0),
            "conexoes": {
                "ativas":      connections.get("current", 0),
                "disponiveis": connections.get("available", 0),
                "total_criadas": connections.get("totalCreated", 0),
            },
            "operacoes": {
                "insert":  opcounters.get("insert", 0),
                "query":   opcounters.get("query",  0),
                "update":  opcounters.get("update", 0),
                "delete":  opcounters.get("delete", 0),
                "command": opcounters.get("command", 0),
            },
            "memoria_mongo_mb": {
                "residente": mem.get("resident", 0),
                "virtual":   mem.get("virtual", 0),
            },
            "rede": {
                "bytes_in":     network.get("bytesIn", 0),
                "bytes_out":    network.get("bytesOut", 0),
                "num_requests": network.get("numRequests", 0),
            },
            "colecoes": colecoes,
        }
    except Exception as e:
        resultado["banco"] = {"status": "Erro", "detalhe": str(e)}

    # ── Métricas de negócio ──────────────────────────────────
    try:
        from src.models.dim_solicitacao import StatusSolicitacao as SS
        sol_pendentes  = await db.dim_solicitacao_cadastro.count_documents({"status": SS.PENDENTE})
        evol_pendentes = await db.fato_evolucao.count_documents({"status": "Pendente de Revisão"})
        rels_aguardando = await db.fato_relatorio.count_documents({"status": "Aguardando Assinatura do Docente"})
        rels_finalizados = await db.fato_relatorio.count_documents({"status": "Finalizado"})

        usuarios_por_perfil: dict = {}
        async for u in db.dim_usuario.find({}, {"perfil": 1, "is_ativo": 1}):
            chave = u.get("perfil", "Desconhecido")
            usuarios_por_perfil[chave] = usuarios_por_perfil.get(chave, 0) + 1

        resultado["negocio"] = {
            "solicitacoes_pendentes":  sol_pendentes,
            "evolucoes_pendentes":     evol_pendentes,
            "relatorios_aguardando":   rels_aguardando,
            "relatorios_finalizados":  rels_finalizados,
            "usuarios_por_perfil":     usuarios_por_perfil,
        }
    except Exception:
        resultado["negocio"] = {}

    return resultado


def _formatar_uptime(segundos: int) -> str:
    if segundos < 60:
        return f"{segundos}s"
    minutos, s = divmod(segundos, 60)
    horas, m   = divmod(minutos, 60)
    dias, h    = divmod(horas, 24)
    if dias:
        return f"{dias}d {h}h {m}m"
    if h:
        return f"{h}h {m}m"
    return f"{m}m {s}s"


# ==========================================
# 2. GESTÃO DE USUÁRIOS (CRUD COMPLETO)
# ==========================================
@router.get("/usuarios", response_model=List[UsuarioResponse], dependencies=[Depends(verificar_admin)])
async def listar_usuarios(
    perfil: Optional[TipoPerfil] = Query(None),
    is_ativo: Optional[bool] = Query(None),
    db = Depends(get_database)
):
    filtro = {}
    if perfil: filtro["perfil"] = perfil
    if is_ativo is not None: filtro["is_ativo"] = is_ativo
    
    cursor = db.dim_usuario.find(filtro).sort("nome_completo", 1)
    
    # Aqui mantemos o limite no to_list para proteger a API caso tentem listar 10.000 usuários na tela de uma vez
    usuarios = await cursor.to_list(length=500)
    for u in usuarios: u["_id"] = str(u["_id"])
    return usuarios

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
async def criar_usuario(usuario_in: UsuarioCreate, db = Depends(get_database)):
    # Verifica se a matrícula ou email já existem
    if await db.dim_usuario.find_one({"matricula": usuario_in.matricula}):
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada.")
    if await db.dim_usuario.find_one({"email": usuario_in.email}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    # Cria o Hash da senha
    senha_hasheada = get_password_hash(usuario_in.senha)
    
    # Monta o dicionário mesclando os dados com a senha hasheada (remove a senha em texto plano)
    dados_db = usuario_in.model_dump(exclude={"senha"})
    dados_db["senha_hash"] = senha_hasheada
    
    novo_usuario = DimUsuario(**dados_db)
    resultado = await db.dim_usuario.insert_one(novo_usuario.model_dump(by_alias=True, exclude_none=True))
    
    usuario_criado = await db.dim_usuario.find_one({"_id": resultado.inserted_id})
    usuario_criado["_id"] = str(usuario_criado["_id"])
    return usuario_criado

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse, dependencies=[Depends(verificar_admin)])
async def atualizar_usuario(usuario_id: str, obj_in: UsuarioUpdate, db = Depends(get_database)):
    update_data = obj_in.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado para atualização.")
        
    resultado = await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, {"$set": update_data}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    usuario = await db.dim_usuario.find_one({"_id": ObjectId(usuario_id)})
    usuario["_id"] = str(usuario["_id"])
    return usuario

@router.patch("/usuarios/{usuario_id}/reset-password", dependencies=[Depends(verificar_admin)])
async def resetar_senha_usuario(usuario_id: str, db = Depends(get_database)):
    # Gera uma senha aleatória provisória de 8 caracteres
    nova_senha_temp = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    senha_hash = get_password_hash(nova_senha_temp)
    
    # Atualiza a senha e ARMA A ARMADILHA obrigando a troca no próximo login!
    resultado = await db.dim_usuario.update_one(
        {"_id": ObjectId(usuario_id)}, 
        {"$set": {
            "senha_hash": senha_hash,
            "precisa_trocar_senha": True
        }}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return {"nova_senha": nova_senha_temp}

# ==========================================
# 3. SOLICITAÇÕES DE CADASTRO (Caixa de Entrada)
# ==========================================
@router.get("/solicitacoes", response_model=List[SolicitacaoResponse], dependencies=[Depends(verificar_admin)])
async def listar_solicitacoes(
    status_filter: Optional[StatusSolicitacao] = Query(None, alias="status"),
    db = Depends(get_database),
):
    filtro: dict = {}
    if status_filter:
        filtro["status"] = status_filter
    else:
        filtro["status"] = StatusSolicitacao.PENDENTE

    cursor = db.dim_solicitacao_cadastro.find(filtro).sort("criado_em", -1)
    solicitacoes = await cursor.to_list(length=200)
    for s in solicitacoes:
        s["_id"] = str(s["_id"])
    return solicitacoes


@router.get("/solicitacoes/contagem", dependencies=[Depends(verificar_admin)])
async def contar_solicitacoes_pendentes(db = Depends(get_database)):
    count = await db.dim_solicitacao_cadastro.count_documents({"status": StatusSolicitacao.PENDENTE})
    return {"pendentes": count}


@router.patch("/solicitacoes/{sol_id}/aprovar", response_model=UsuarioResponse, dependencies=[Depends(verificar_admin)])
async def aprovar_solicitacao(
    sol_id: str,
    edits: SolicitacaoAprovar,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Aprova solicitação criando o usuário definitivo. Admin pode editar campos."""
    sol = await db.dim_solicitacao_cadastro.find_one({"_id": ObjectId(sol_id)})
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    if sol.get("status") != StatusSolicitacao.PENDENTE:
        raise HTTPException(status_code=400, detail="Esta solicitação já foi processada.")

    # Aplica edições do admin (se enviadas)
    nome    = (edits.nome_completo     or sol["nome_completo"]).strip()
    email   = edits.email              or sol["email"]
    perfil  = edits.perfil_solicitado  or sol["perfil_solicitado"]
    area    = edits.area_atendimento   if edits.area_atendimento is not None else sol.get("area_atendimento")

    if perfil == TipoPerfil.ESTAGIARIO and not area:
        raise HTTPException(status_code=400, detail="Defina a área de atendimento para Estagiário.")

    # Valida unicidade no momento da aprovação (estado pode ter mudado)
    if await db.dim_usuario.find_one({"matricula": sol["matricula"]}):
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada por outro usuário.")
    if await db.dim_usuario.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado por outro usuário.")

    novo = DimUsuario(
        nome_completo    = nome,
        matricula        = sol["matricula"],
        email            = email,
        senha_hash       = sol["senha_hash"],
        perfil           = perfil,
        area_atendimento = area if perfil == TipoPerfil.ESTAGIARIO else None,
        is_ativo         = True,
        precisa_trocar_senha = False,
    )
    res = await db.dim_usuario.insert_one(novo.model_dump(by_alias=True, exclude_none=True))

    await db.dim_solicitacao_cadastro.update_one(
        {"_id": ObjectId(sol_id)},
        {"$set": {
            "status":         StatusSolicitacao.APROVADA,
            "revisado_por_id": str(current_user["_id"]),
            "revisado_em":    datetime.now(timezone.utc),
            "atualizado_em":  datetime.now(timezone.utc),
        }},
    )

    criado = await db.dim_usuario.find_one({"_id": res.inserted_id})
    criado["_id"] = str(criado["_id"])
    return criado


@router.patch("/solicitacoes/{sol_id}/recusar", dependencies=[Depends(verificar_admin)])
async def recusar_solicitacao(
    sol_id: str,
    payload: SolicitacaoRecusar,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Recusa a solicitação registrando o motivo (não exclui o registro, mantém auditoria)."""
    sol = await db.dim_solicitacao_cadastro.find_one({"_id": ObjectId(sol_id)})
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    if sol.get("status") != StatusSolicitacao.PENDENTE:
        raise HTTPException(status_code=400, detail="Esta solicitação já foi processada.")

    await db.dim_solicitacao_cadastro.update_one(
        {"_id": ObjectId(sol_id)},
        {"$set": {
            "status":         StatusSolicitacao.RECUSADA,
            "motivo_recusa":  payload.motivo_recusa,
            "revisado_por_id": str(current_user["_id"]),
            "revisado_em":    datetime.now(timezone.utc),
            "atualizado_em":  datetime.now(timezone.utc),
        }},
    )
    return {"message": "Solicitação recusada."}


@router.get("/estagiarios", response_model=List[UsuarioResponse])
async def listar_estagiarios_ativos(db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    """Rota pública (qualquer logado) para listar estagiários ativos."""
    if current_user.get("perfil") not in [TipoPerfil.ADMINISTRADOR, TipoPerfil.DOCENTE]:
        raise HTTPException(status_code=403, detail="Acesso negado.")
    
    cursor = db.dim_usuario.find({
        "perfil": TipoPerfil.ESTAGIARIO,
        "is_ativo": True
    }).sort("nome_completo", 1)
    
    estagiarios = await cursor.to_list(length=500)
    for e in estagiarios:
        e["_id"] = str(e["_id"])
    return estagiarios
