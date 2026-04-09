import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.dim_usuario import TipoPerfil
from src.models.dim_indicador import DirecaoMelhora
from src.models.dim_status import StatusMeta, StatusProntuario


# ── helper: busca CID na base dos 14k, insere se não encontrar ────────────────
async def _get_cid(db, codigo: str, descricao_fallback: str):
    doc = await db.dim_cid.find_one({"codigo": codigo})
    if doc:
        print(f"  ✅ CID {codigo} encontrado na base")
        return doc["_id"]
    res = await db.dim_cid.insert_one({
        "codigo": codigo, "descricao": descricao_fallback,
        "is_ativo": True,
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc),
    })
    print(f"  ⚠️  CID {codigo} não encontrado — inserido manualmente")
    return res.inserted_id


async def rodar_seed():
    print("🌱 Iniciando seed do ProntuSMART...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # ── Limpa coleções — dim_cid PRESERVADA (14k registros) ──────────────────
    colecoes = [
        "dim_usuario", "dim_area", "dim_indicador",
        "dim_paciente", "fato_prontuario", "fato_meta_smart",
        "fato_evolucao", "fato_medicao",
    ]
    for col in colecoes:
        await db[col].drop()
        print(f"  🗑️  Coleção '{col}' limpa")
    print("  ⚠️  dim_cid preservada (14k registros mantidos)")

    agora = datetime.now(timezone.utc)

    # ── 1. ÁREAS ─────────────────────────────────────────────────────────────
    areas = [
        {"nome": "Saúde da Mulher e do Homem",  "descricao": "Fisioterapia pélvica e saúde preventiva",       "icone": "ph:person-simple-walk-bold", "cor": "rose",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Geriatria",                    "descricao": "Saúde do idoso e prevenção de quedas",          "icone": "ph:wheelchair-bold",         "cor": "amber",   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Neurologia Adulto",            "descricao": "Reabilitação neurofuncional para adultos",      "icone": "ph:brain-bold",              "cor": "purple",  "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Neuropediatria",               "descricao": "Reabilitação neurofuncional pediátrica",        "icone": "ph:baby-bold",               "cor": "cyan",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Traumato-Ortopedia",           "descricao": "Reabilitação de fraturas e lesões",             "icone": "ph:bone-bold",               "cor": "blue",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Cardiorrespiratória",          "descricao": "Reabilitação cardíaca e pulmonar",              "icone": "ph:lungs-bold",              "cor": "emerald", "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for a in areas:
        await db.dim_area.insert_one(a)
    print(f"  ✅ {len(areas)} Áreas cadastradas")

    # ── 2. INDICADORES ────────────────────────────────────────────────────────
    indicadores = [
        {"nome": "Escala Visual Analógica (EVA)",     "unidade_medida": "pontos (0-10)",   "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "descricao": "Intensidade da dor relatada pelo paciente.",                    "areas_vinculadas": ["Todas"],                                                "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Escala de Berg",                    "unidade_medida": "pontos (0-56)",   "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Avalia equilíbrio funcional — ≤45 indica risco de queda.",     "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                       "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Time Up and Go (TUG)",              "unidade_medida": "segundos",        "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "descricao": "Avalia mobilidade, equilíbrio e risco de quedas.",             "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                       "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Distância de Marcha",               "unidade_medida": "metros",          "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Distância percorrida com ou sem dispositivo auxiliar.",        "areas_vinculadas": ["Geriatria", "Neurologia Adulto", "Traumato-Ortopedia"], "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Tempo em Ortostatismo Estável",     "unidade_medida": "segundos",        "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Tempo em pé sem perda de equilíbrio.",                        "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                       "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Força Muscular (Grau 0-5)",         "unidade_medida": "grau",            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Graduação da força muscular por grupo muscular.",              "areas_vinculadas": ["Traumato-Ortopedia", "Neurologia Adulto"],              "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Amplitude de Movimento (ADM)",      "unidade_medida": "graus",           "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Amplitude articular em goniometria.",                         "areas_vinculadas": ["Traumato-Ortopedia"],                                   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "SpO2 em Repouso",                   "unidade_medida": "%",               "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Saturação periférica de oxigênio.",                           "areas_vinculadas": ["Cardiorrespiratória"],                                  "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for ind in indicadores:
        await db.dim_indicador.insert_one(ind)
    print(f"  ✅ {len(indicadores)} Indicadores cadastrados")

    # ── 3. USUÁRIOS ───────────────────────────────────────────────────────────
    senha_hash = get_password_hash("ucb@1234")
    usuarios = [
        {"nome_completo": "Administrador Sistema",       "matricula": "admin01",   "email": "admin@ucb.br",       "senha_hash": senha_hash, "perfil": TipoPerfil.ADMINISTRADOR, "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
        {"nome_completo": "Profa. Ana Lima",             "matricula": "docente01", "email": "ana.lima@ucb.br",    "senha_hash": senha_hash, "perfil": TipoPerfil.DOCENTE,       "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
        {"nome_completo": "João Victor Rodrigues Pinto", "matricula": "est01",     "email": "joao.victor@ucb.br", "senha_hash": senha_hash, "perfil": TipoPerfil.ESTAGIARIO,   "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
        {"nome_completo": "Maria Eduarda Santos",        "matricula": "est02",     "email": "m.eduarda@ucb.br",   "senha_hash": senha_hash, "perfil": TipoPerfil.ESTAGIARIO,   "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
    ]
    ids_u: dict = {}
    for u in usuarios:
        res = await db.dim_usuario.insert_one(u)
        ids_u[u["matricula"]] = res.inserted_id
    print(f"  ✅ {len(usuarios)} Usuários cadastrados")

    docente_id = ids_u["docente01"]
    est01_id   = ids_u["est01"]   # João Victor
    est02_id   = ids_u["est02"]   # Maria Eduarda

    # ── 4. PACIENTES ──────────────────────────────────────────────────────────
    pacientes_data = [
        # Paciente 1 — existente, mantido idêntico
        {
            "nome_completo": "Carlos Alberto Ferreira", "cpf": "123.456.789-00",
            "data_nascimento": "1958-03-12", "sexo": "Masculino",
            "telefone_contato": "(61) 98765-4321", "email": "carlos.ferreira@email.com",
            "endereco_resumido": "QNM 38 Conjunto I, Ceilândia - DF",
            "area_atendimento_atual": "Neurologia Adulto",
            "queixa_principal": "Dificuldade para andar sozinho dentro de casa",
            "is_ativo": True, "criado_em": agora - timedelta(days=30), "atualizado_em": agora,
        },
        # Paciente 2 — Geriatria, dor registrada → alerta de risco
        {
            "nome_completo": "Maria das Graças Oliveira", "cpf": "234.567.890-11",
            "data_nascimento": "1945-07-22", "sexo": "Feminino",
            "telefone_contato": "(61) 91234-5678", "email": "mgraca@email.com",
            "endereco_resumido": "SQN 315 Bloco C, Asa Norte - DF",
            "area_atendimento_atual": "Geriatria",
            "queixa_principal": "Dor lombar crônica com dificuldade de deambulação",
            "is_ativo": True, "criado_em": agora - timedelta(days=45), "atualizado_em": agora,
        },
        # Paciente 3 — Traumato-Ortopedia, pós-operatório
        {
            "nome_completo": "Roberto Lima da Silva", "cpf": "345.678.901-22",
            "data_nascimento": "1962-11-05", "sexo": "Masculino",
            "telefone_contato": "(61) 99876-5432", "email": "roberto.lima@email.com",
            "endereco_resumido": "QI 25 Conjunto 12, Guará - DF",
            "area_atendimento_atual": "Traumato-Ortopedia",
            "queixa_principal": "Limitação de movimentos e dor no quadril esquerdo pós-fratura",
            "is_ativo": True, "criado_em": agora - timedelta(days=20), "atualizado_em": agora,
        },
        # Paciente 4 — Cardiorrespiratória, DPOC
        {
            "nome_completo": "Sandra Costa Mendes", "cpf": "456.789.012-33",
            "data_nascimento": "1955-02-18", "sexo": "Feminino",
            "telefone_contato": "(61) 98888-1122", "email": "sandra.costa@email.com",
            "endereco_resumido": "SHIS QI 11 Conjunto 4, Lago Sul - DF",
            "area_atendimento_atual": "Cardiorrespiratória",
            "queixa_principal": "Dispneia aos médios esforços e dessaturação",
            "is_ativo": True, "criado_em": agora - timedelta(days=15), "atualizado_em": agora,
        },
    ]
    ids_pac = []
    for p in pacientes_data:
        res = await db.dim_paciente.insert_one(p)
        ids_pac.append(res.inserted_id)
    print(f"  ✅ {len(pacientes_data)} Pacientes cadastrados")

    pac1_id, pac2_id, pac3_id, pac4_id = ids_pac

    # ── 5. CIDs ───────────────────────────────────────────────────────────────
    cid1_id = await _get_cid(db, "I63.9",  "Acidente vascular cerebral isquêmico, não especificado")
    cid2_id = await _get_cid(db, "M54.5",  "Dor lombar")
    cid3_id = await _get_cid(db, "S72.0",  "Fratura do colo do fêmur")
    cid4_id = await _get_cid(db, "J44.1",  "Doença pulmonar obstrutiva crônica com exacerbação aguda")

    # ── 6. INDICADORES (busca IDs pelo nome) ──────────────────────────────────
    async def ind(nome):
        doc = await db.dim_indicador.find_one({"nome": nome})
        assert doc is not None, f"Indicador '{nome}' não encontrado!"
        return doc["_id"]

    ind_distancia = await ind("Distância de Marcha")
    ind_berg      = await ind("Escala de Berg")
    ind_tug       = await ind("Time Up and Go (TUG)")
    ind_adm       = await ind("Amplitude de Movimento (ADM)")
    ind_forca     = await ind("Força Muscular (Grau 0-5)")
    ind_spo2      = await ind("SpO2 em Repouso")

    # ── 7. PRONTUÁRIOS ────────────────────────────────────────────────────────

    # Prontuário 1 — Carlos Alberto (Neurologia Adulto) — est01, dor: False
    pront1 = {
        "paciente_id": str(pac1_id), "estagiario_id": str(est01_id),
        "docente_id":  str(docente_id), "cid_id": str(cid1_id),
        "area_atendimento": "Neurologia Adulto",
        "numero_prontuario": f"UCB-{agora.year}-00001",
        "status": StatusProntuario.ATIVO,
        "total_sessoes": 3, "data_ultima_evolucao": agora - timedelta(days=2),
        "diagnostico_medico":           "Acidente vascular cerebral isquêmico",
        "diagnostico_fisioterapeutico": "Déficit de mobilidade funcional com prejuízo de marcha, transferências e equilíbrio",
        "queixa_principal":             "Dificuldade para andar sozinho dentro de casa",
        "objetivo_paciente":            "Conseguir ir sozinho ao banheiro",
        "tempo_evolucao": "3 meses", "comorbidades": "HAS e DM tipo 2",
        "medicamentos": "Losartana, metformina, AAS", "dispositivo_auxiliar": "Andador",
        "barreiras_ambientais": "Casa com corredor estreito e banheiro sem barra de apoio",
        "sedestacao": "Independente", "ortostatismo": "Supervisão",
        "transferencias": "Ajuda parcial", "realiza_marcha": True,
        "marcha_dispositivo": True, "distancia_tolerada": "5 metros",
        "funcao_mmss": "Parcialmente comprometida", "funcao_mmii": "Parcialmente comprometida",
        "equilibrio": "Alterado", "risco_queda": "Alto",
        "dor": False,  # sem alerta de dor
        "fadiga_funcional": True, "compreende_comandos": True, "comunicacao_preservada": True,
        "avd_banho": "AP", "avd_vestir": "AP", "avd_higiene": "AP",
        "avd_locomocao": "D", "avd_alimentacao": "I", "avd_banheiro": "AP",
        "atividade_mais_impactada": "Locomoção dentro de casa",
        "principal_limitacao": "Não consegue caminhar com segurança sem auxílio",
        "teste_escala_principal": "Escala de Berg", "valor_teste_inicial": "28 pontos",
        "problema_funcional_prioritario": "Déficit de marcha com risco aumentado de queda",
        "atividade_comprometida": "Locomoção domiciliar",
        "impacto_independencia": "Dependência parcial para deslocamento",
        "prioridade_terapeutica": "Melhorar marcha funcional e segurança nas transferências",
        "criado_em": agora - timedelta(days=30), "atualizado_em": agora,
    }

    # Prontuário 2 — Maria das Graças (Geriatria) — est02, dor: True → alerta
    pront2 = {
        "paciente_id": str(pac2_id), "estagiario_id": str(est02_id),
        "docente_id":  str(docente_id), "cid_id": str(cid2_id),
        "area_atendimento": "Geriatria",
        "numero_prontuario": f"UCB-{agora.year}-00002",
        "status": StatusProntuario.ATIVO,
        "total_sessoes": 4, "data_ultima_evolucao": agora - timedelta(days=3),
        "diagnostico_medico":           "Lombalgia crônica com irradiação para MMII",
        "diagnostico_fisioterapeutico": "Síndrome dolorosa lombar com limitação de marcha",
        "queixa_principal":             "Dor lombar crônica com dificuldade de deambulação",
        "objetivo_paciente":            "Caminhar sem dor até a padaria do bairro",
        "tempo_evolucao": "6 meses", "comorbidades": "Osteoporose e artrose bilateral de joelhos",
        "medicamentos": "Ibuprofeno, cálcio + vitamina D", "dispositivo_auxiliar": "Bengala",
        "barreiras_ambientais": "Escadas sem corrimão, calçadas irregulares",
        "sedestacao": "Independente com dor", "ortostatismo": "Independente com dor",
        "transferencias": "Independente", "realiza_marcha": True,
        "marcha_dispositivo": True, "distancia_tolerada": "50 metros",
        "funcao_mmss": "Preservada", "funcao_mmii": "Comprometida por dor",
        "equilibrio": "Levemente alterado", "risco_queda": "Moderado",
        "dor": True,  # ← ALERTA DE RISCO: dor registrada
        "dor_intensidade_local": "7/10 — região lombar baixa com irradiação para glúteos",
        "fadiga_funcional": True, "compreende_comandos": True, "comunicacao_preservada": True,
        "avd_banho": "I", "avd_vestir": "I", "avd_higiene": "I",
        "avd_locomocao": "AP", "avd_alimentacao": "I", "avd_banheiro": "I",
        "atividade_mais_impactada": "Caminhada comunitária",
        "principal_limitacao": "Dor limita distância percorrida e velocidade de marcha",
        "teste_escala_principal": "Time Up and Go (TUG)", "valor_teste_inicial": "22 segundos",
        "problema_funcional_prioritario": "Síndrome dolorosa lombar com limitação de mobilidade funcional",
        "atividade_comprometida": "Deambulação comunitária",
        "impacto_independencia": "Restrição à participação em atividades sociais e domésticas",
        "prioridade_terapeutica": "Redução da dor e melhora da tolerância à marcha",
        "criado_em": agora - timedelta(days=45), "atualizado_em": agora,
    }

    # Prontuário 3 — Roberto Lima (Traumato-Ortopedia) — est01
    pront3 = {
        "paciente_id": str(pac3_id), "estagiario_id": str(est01_id),
        "docente_id":  str(docente_id), "cid_id": str(cid3_id),
        "area_atendimento": "Traumato-Ortopedia",
        "numero_prontuario": f"UCB-{agora.year}-00003",
        "status": StatusProntuario.ATIVO,
        "total_sessoes": 2, "data_ultima_evolucao": agora - timedelta(days=5),
        "diagnostico_medico":           "Fratura do colo do fêmur esquerdo — pós-artroplastia total de quadril",
        "diagnostico_fisioterapeutico": "Limitação de ADM de quadril e déficit de força em MMII",
        "queixa_principal":             "Limitação de movimentos e dor no quadril esquerdo pós-operatória",
        "objetivo_paciente":            "Voltar a subir escadas e jogar dominó com os amigos",
        "tempo_evolucao": "1 mês", "comorbidades": "HAS",
        "medicamentos": "Anlodipino, anticoagulante oral", "dispositivo_auxiliar": "Muleta axilar bilateral",
        "barreiras_ambientais": "Banheiro sem adaptação, quarto no 1º andar",
        "sedestacao": "Independente", "ortostatismo": "Supervisão",
        "transferencias": "Ajuda parcial", "realiza_marcha": True,
        "marcha_dispositivo": True, "distancia_tolerada": "20 metros",
        "funcao_mmss": "Preservada", "funcao_mmii": "Comprometida à esquerda",
        "equilibrio": "Alterado", "risco_queda": "Alto",
        "dor": True,
        "dor_intensidade_local": "5/10 — região inguinal esquerda",
        "fadiga_funcional": False, "compreende_comandos": True, "comunicacao_preservada": True,
        "avd_banho": "AP", "avd_vestir": "AP", "avd_higiene": "I",
        "avd_locomocao": "AP", "avd_alimentacao": "I", "avd_banheiro": "AP",
        "atividade_mais_impactada": "Subir e descer escadas",
        "principal_limitacao": "Limitação de flexão de quadril e déficit de força de abdutores",
        "teste_escala_principal": "Amplitude de Movimento (ADM)", "valor_teste_inicial": "45 graus",
        "problema_funcional_prioritario": "Déficit de ADM e força em MMII pós-artroplastia",
        "atividade_comprometida": "Subir escadas e transferências",
        "impacto_independencia": "Dependência parcial para AVDs e locomoção",
        "prioridade_terapeutica": "Ganho de ADM, força e marcha segura",
        "criado_em": agora - timedelta(days=20), "atualizado_em": agora,
    }

    # Prontuário 4 — Sandra Costa (Cardiorrespiratória) — est02
    pront4 = {
        "paciente_id": str(pac4_id), "estagiario_id": str(est02_id),
        "docente_id":  str(docente_id), "cid_id": str(cid4_id),
        "area_atendimento": "Cardiorrespiratória",
        "numero_prontuario": f"UCB-{agora.year}-00004",
        "status": StatusProntuario.ATIVO,
        "total_sessoes": 2, "data_ultima_evolucao": agora - timedelta(days=4),
        "diagnostico_medico":           "DPOC grau III (GOLD) com histórico de exacerbações frequentes",
        "diagnostico_fisioterapeutico": "Limitação ventilatória com intolerância ao esforço",
        "queixa_principal":             "Dispneia aos médios esforços e dessaturação",
        "objetivo_paciente":            "Conseguir varrer a casa sem parar para descansar",
        "tempo_evolucao": "2 anos", "comorbidades": "Tabagismo cessante, HAS",
        "medicamentos": "Formoterol + budesonida inalatória, salbutamol SOS",
        "dispositivo_auxiliar": "Oxigênio domiciliar noturno",
        "barreiras_ambientais": "Apartamento sem elevador, 2º andar",
        "sedestacao": "Independente", "ortostatismo": "Independente",
        "transferencias": "Independente", "realiza_marcha": True,
        "marcha_dispositivo": False, "distancia_tolerada": "100 metros",
        "funcao_mmss": "Preservada", "funcao_mmii": "Preservada",
        "equilibrio": "Preservado", "risco_queda": "Baixo",
        "dor": False, "fadiga_funcional": True,
        "compreende_comandos": True, "comunicacao_preservada": True,
        "avd_banho": "I", "avd_vestir": "I", "avd_higiene": "I",
        "avd_locomocao": "AP", "avd_alimentacao": "I", "avd_banheiro": "I",
        "atividade_mais_impactada": "Tarefas domésticas contínuas",
        "principal_limitacao": "Dispneia limita esforços sustentados",
        "teste_escala_principal": "SpO2 em Repouso", "valor_teste_inicial": "91%",
        "problema_funcional_prioritario": "Limitação ventilatória com impacto nas AVDs",
        "atividade_comprometida": "Tarefas domésticas e locomoção no andar",
        "impacto_independencia": "Independente mas com limitação significativa de esforço",
        "prioridade_terapeutica": "Melhora da capacidade ventilatória e tolerância ao esforço",
        "criado_em": agora - timedelta(days=15), "atualizado_em": agora,
    }

    ids_pront = []
    for p in [pront1, pront2, pront3, pront4]:
        res = await db.fato_prontuario.insert_one(p)
        ids_pront.append(res.inserted_id)
    pront1_id, pront2_id, pront3_id, pront4_id = ids_pront
    print(f"  ✅ {len(ids_pront)} Prontuários criados")

    # ── 8. METAS SMART ────────────────────────────────────────────────────────

    metas = [
        # Pront1 — Carlos Alberto — Meta 1: Distância de Marcha (em andamento, futura)
        {
            "prontuario_id": str(pront1_id), "indicador_id": str(ind_distancia),
            "estagiario_id": str(est01_id),
            "problema_relacionado": "Déficit de marcha",
            "especifico": "Melhorar a capacidade de marcha em ambiente domiciliar",
            "criterio_mensuravel": "Caminhar 10 metros sem pausa",
            "valor_inicial": 5.0, "valor_alvo": 10.0,
            "condicao_execucao": "Com andador e supervisão",
            "alcancavel": "Musculatura preservada com potencial de ganho funcional",
            "relevante": "Permitir deslocamento até o banheiro com mais independência",
            "data_limite": agora + timedelta(days=28),
            "data_reavaliacao": agora + timedelta(days=28),
            "status": StatusMeta.EM_ANDAMENTO, "progresso_percentual": 60.0,
            "historico_alteracoes": [], "criado_em": agora - timedelta(days=30), "atualizado_em": agora,
        },
        # Pront1 — Carlos Alberto — Meta 2: Escala de Berg (em andamento, futura)
        {
            "prontuario_id": str(pront1_id), "indicador_id": str(ind_berg),
            "estagiario_id": str(est01_id),
            "problema_relacionado": "Déficit de equilíbrio",
            "especifico": "Melhorar equilíbrio em ortostatismo",
            "criterio_mensuravel": "Atingir ≥ 45 pontos na Escala de Berg",
            "valor_inicial": 28.0, "valor_alvo": 45.0,
            "condicao_execucao": "Sem apoio manual constante",
            "alcancavel": "Potencial de ganho com treino específico",
            "relevante": "Aumentar segurança para transferências e higiene pessoal",
            "data_limite": agora + timedelta(days=42),
            "data_reavaliacao": agora + timedelta(days=42),
            "status": StatusMeta.EM_ANDAMENTO, "progresso_percentual": 47.0,
            "historico_alteracoes": [], "criado_em": agora - timedelta(days=30), "atualizado_em": agora,
        },
        # Pront2 — Maria das Graças — Meta TUG: ATRASADA + progresso < 30% → alerta
        {
            "prontuario_id": str(pront2_id), "indicador_id": str(ind_tug),
            "estagiario_id": str(est02_id),
            "problema_relacionado": "Dificuldade de marcha por dor",
            "especifico": "Reduzir o tempo no TUG para melhorar mobilidade funcional",
            "criterio_mensuravel": "Completar TUG em ≤ 14 segundos",
            "valor_inicial": 22.0, "valor_alvo": 14.0,
            "condicao_execucao": "Com bengala, sem analgésico prévio",
            "alcancavel": "Redução esperada com controle da dor e fortalecimento",
            "relevante": "TUG ≤ 14s indica marcha segura e independente na comunidade",
            "data_limite": agora - timedelta(days=14),  # ← PASSADA — meta atrasada
            "data_reavaliacao": agora + timedelta(days=7),
            "status": StatusMeta.EM_ANDAMENTO, "progresso_percentual": 15.0,  # ← < 30% — estagnada
            "historico_alteracoes": [], "criado_em": agora - timedelta(days=45), "atualizado_em": agora,
        },
        # Pront3 — Roberto Lima — ADM de quadril
        {
            "prontuario_id": str(pront3_id), "indicador_id": str(ind_adm),
            "estagiario_id": str(est01_id),
            "problema_relacionado": "Limitação de ADM pós-artroplastia",
            "especifico": "Recuperar amplitude de movimento de flexão de quadril esquerdo",
            "criterio_mensuravel": "Atingir 90 graus de flexão de quadril",
            "valor_inicial": 45.0, "valor_alvo": 90.0,
            "condicao_execucao": "Respeitando restrições pós-operatórias (sem flexão > 90° e adução)",
            "alcancavel": "Prótese bem posicionada, sem complicações cirúrgicas",
            "relevante": "90° é o mínimo necessário para sentar sem adaptação",
            "data_limite": agora + timedelta(days=56),
            "data_reavaliacao": agora + timedelta(days=28),
            "status": StatusMeta.EM_ANDAMENTO, "progresso_percentual": 33.0,
            "historico_alteracoes": [], "criado_em": agora - timedelta(days=20), "atualizado_em": agora,
        },
        # Pront4 — Sandra Costa — SpO2
        {
            "prontuario_id": str(pront4_id), "indicador_id": str(ind_spo2),
            "estagiario_id": str(est02_id),
            "problema_relacionado": "Dessaturação ao esforço",
            "especifico": "Melhorar saturação periférica de oxigênio em repouso",
            "criterio_mensuravel": "SpO2 ≥ 94% em repouso sem oxigênio suplementar",
            "valor_inicial": 91.0, "valor_alvo": 94.0,
            "condicao_execucao": "Em repouso, sem uso de O2",
            "alcancavel": "Resposta esperada com reeducação respiratória e técnicas de clearance",
            "relevante": "SpO2 ≥ 94% reduz risco de complicações e melhora disposição",
            "data_limite": agora + timedelta(days=60),
            "data_reavaliacao": agora + timedelta(days=30),
            "status": StatusMeta.EM_ANDAMENTO, "progresso_percentual": 25.0,
            "historico_alteracoes": [], "criado_em": agora - timedelta(days=15), "atualizado_em": agora,
        },
    ]
    await db.fato_meta_smart.insert_many(metas)
    print(f"  ✅ {len(metas)} Metas SMART criadas")

    # ── 9. EVOLUÇÕES ──────────────────────────────────────────────────────────

    evolucoes = [
        # ── João Victor (est01) / Pront1 Carlos Alberto ─────────────────────
        {
            "prontuario_id": str(pront1_id), "autor_id": str(est01_id),
            "texto_clinico": (
                "S - Paciente refere leve melhora na disposição. Relata ter conseguido ir ao banheiro "
                "sozinho na noite anterior com auxílio do andador.\n"
                "O - Marcha realizada com andador, percorrendo 7m sem pausas. Equilíbrio estático melhorado.\n"
                "A - Evolução positiva. Paciente demonstra motivação e engajamento.\n"
                "P - Progredir distância de marcha para 8m e iniciar treino de equilíbrio dinâmico."
            ),
            "medicoes": [
                {"indicador_id": str(ind_distancia), "nome_indicador": "Distância de Marcha",
                 "valor_registrado": "7", "unidade": "metros"},
                {"indicador_id": str(ind_berg), "nome_indicador": "Escala de Berg",
                 "valor_registrado": "34", "unidade": "pontos (0-56)"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_id),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=21),
        },
        {
            "prontuario_id": str(pront1_id), "autor_id": str(est01_id),
            "texto_clinico": (
                "S - Paciente relata melhora significativa na confiança ao caminhar. Realizou a higiene "
                "pessoal sem ajuda pela primeira vez desde o AVC.\n"
                "O - Marcha com andador percorrendo 8,5m. Berg = 38 pontos. Transferências com supervisão mínima.\n"
                "A - Evolução expressiva. Meta de distância praticamente atingida.\n"
                "P - Tentar alcançar 10m na próxima sessão. Iniciar treino sem andador com apoio de parede."
            ),
            "medicoes": [
                {"indicador_id": str(ind_distancia), "nome_indicador": "Distância de Marcha",
                 "valor_registrado": "8.5", "unidade": "metros"},
                {"indicador_id": str(ind_berg), "nome_indicador": "Escala de Berg",
                 "valor_registrado": "38", "unidade": "pontos (0-56)"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_id),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=10),
        },
        {
            "prontuario_id": str(pront1_id), "autor_id": str(est01_id),
            "texto_clinico": (
                "S - Paciente muito motivado. Relata que caminhou até o quintal ontem.\n"
                "O - Marcha com andador 10m concluída. Berg = 42 pontos. Risco de queda reduzido.\n"
                "A - Meta de marcha praticamente atingida. Equilíbrio ainda abaixo do alvo (45 pts).\n"
                "P - Consolidar ganhos de marcha. Focar no treino de equilíbrio para atingir 45 pts Berg."
            ),
            "medicoes": [
                {"indicador_id": str(ind_distancia), "nome_indicador": "Distância de Marcha",
                 "valor_registrado": "10", "unidade": "metros"},
                {"indicador_id": str(ind_berg), "nome_indicador": "Escala de Berg",
                 "valor_registrado": "42", "unidade": "pontos (0-56)"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=2),
        },

        # ── João Victor (est01) / Pront3 Roberto Lima ────────────────────────
        {
            "prontuario_id": str(pront3_id), "autor_id": str(est01_id),
            "texto_clinico": (
                "S - Paciente relata dor EVA 5/10 na região inguinal ao movimento. Refere progresso na "
                "independência para sentar-se.\n"
                "O - ADM de flexão de quadril esquerdo: 60°. Força abdutor: grau 3+. Marcha com muletas estável.\n"
                "A - Boa evolução considerando o pós-operatório recente. Sem sinais de complicações.\n"
                "P - Progredir ADM para 75°. Iniciar exercícios em cadeia cinética fechada."
            ),
            "medicoes": [
                {"indicador_id": str(ind_adm), "nome_indicador": "Amplitude de Movimento (ADM)",
                 "valor_registrado": "60", "unidade": "graus"},
                {"indicador_id": str(ind_forca), "nome_indicador": "Força Muscular (Grau 0-5)",
                 "valor_registrado": "3", "unidade": "grau"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_id),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=12),
        },
        {
            "prontuario_id": str(pront3_id), "autor_id": str(est01_id),
            "texto_clinico": (
                "S - Paciente relata dor 3/10, com melhora significativa. Está conseguindo sentar sem dor.\n"
                "O - ADM flexão de quadril: 75°. Força: grau 4. Marcha com 1 muleta por curtos períodos.\n"
                "A - Evolução muito positiva. Ritmo de recuperação acima do esperado.\n"
                "P - Progredir para 90° de flexão. Treino de subida/descida de degrau baixo."
            ),
            "medicoes": [
                {"indicador_id": str(ind_adm), "nome_indicador": "Amplitude de Movimento (ADM)",
                 "valor_registrado": "75", "unidade": "graus"},
                {"indicador_id": str(ind_forca), "nome_indicador": "Força Muscular (Grau 0-5)",
                 "valor_registrado": "4", "unidade": "grau"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=5),
        },

        # ── Maria Eduarda (est02) / Pront2 Maria das Graças ─────────────────
        {
            "prontuario_id": str(pront2_id), "autor_id": str(est02_id),
            "texto_clinico": (
                "S - Paciente relata dor persistente 7/10 em repouso e 9/10 ao caminhar. Sem melhora "
                "perceptível desde o início do tratamento.\n"
                "O - TUG: 20 segundos. Marcha antálgica com bengala. ADM lombar limitado por dor.\n"
                "A - Evolução aquém do esperado. Dor persiste intensa limitando a progressão.\n"
                "P - Rever conduta analgésica. Priorizar técnicas de controle de dor antes de progredir marcha."
            ),
            "medicoes": [
                {"indicador_id": str(ind_tug), "nome_indicador": "Time Up and Go (TUG)",
                 "valor_registrado": "20", "unidade": "segundos"},
            ],
            "status": "Ajustes Solicitados",
            "docente_revisor_id": str(docente_id),
            "feedback_docente": (
                "Boa observação clínica. Inclua na próxima evolução a mensuração da EVA antes e após "
                "a sessão para acompanhar o efeito imediato das técnicas. Descreva também as técnicas "
                "analgésicas utilizadas (TENS, crioterapia, etc.)."
            ),
            "criado_em": agora - timedelta(days=30),
        },
        {
            "prontuario_id": str(pront2_id), "autor_id": str(est02_id),
            "texto_clinico": (
                "S - Paciente relata melhora discreta na dor após TENS. EVA pré-sessão 7/10, pós-sessão 5/10.\n"
                "O - TUG: 19,5 segundos. Aplicação de TENS lombar por 20 min + alongamentos. "
                "Paciente verbalizou alívio durante a sessão.\n"
                "A - Técnica analgésica demonstrou efeito imediato. Progressão lenta mas positiva.\n"
                "P - Manter TENS + iniciar estabilização lombar em decúbito dorsal."
            ),
            "medicoes": [
                {"indicador_id": str(ind_tug), "nome_indicador": "Time Up and Go (TUG)",
                 "valor_registrado": "19.5", "unidade": "segundos"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_id),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=18),
        },
        {
            "prontuario_id": str(pront2_id), "autor_id": str(est02_id),
            "texto_clinico": (
                "S - Paciente relata dor 6/10. Referiu ter conseguido ir à farmácia sozinha durante a semana.\n"
                "O - TUG: 18 segundos. Marcha com bengala mais fluida. Exercícios de estabilização realizados "
                "com boa adesão.\n"
                "A - Progressão lenta porém consistente. Meta de 14s ainda distante, mas tendência positiva.\n"
                "P - Progredir estabilização para sedestação instável. Aumentar tempo de caminhada contínua."
            ),
            "medicoes": [
                {"indicador_id": str(ind_tug), "nome_indicador": "Time Up and Go (TUG)",
                 "valor_registrado": "18", "unidade": "segundos"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=3),
        },

        # ── Maria Eduarda (est02) / Pront4 Sandra Costa ─────────────────────
        {
            "prontuario_id": str(pront4_id), "autor_id": str(est02_id),
            "texto_clinico": (
                "S - Paciente relata dispneia aos médios esforços. Não consegue varrer dois cômodos sem parar.\n"
                "O - SpO2 repouso: 91%. Frequência respiratória: 22 irpm. Padrão respiratório paradoxal observado. "
                "Aplicação de técnicas de drenagem postural e reeducação diafragmática.\n"
                "A - Baseline estabelecido. Capacidade ventilatória comprometida conforme esperado.\n"
                "P - Iniciar treino de músculos respiratórios com threshold. Ensinar posição de alívio da dispneia."
            ),
            "medicoes": [
                {"indicador_id": str(ind_spo2), "nome_indicador": "SpO2 em Repouso",
                 "valor_registrado": "91", "unidade": "%"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_id),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=10),
        },
        {
            "prontuario_id": str(pront4_id), "autor_id": str(est02_id),
            "texto_clinico": (
                "S - Paciente relata leve melhora. Conseguiu varrer um cômodo completo sem parar.\n"
                "O - SpO2 repouso: 92%. FR: 20 irpm. Treino com threshold a 30% da PImáx. "
                "Boa adesão e tolerância ao exercício.\n"
                "A - Evolução inicial positiva. Ganho de 1% na SpO2 em repouso.\n"
                "P - Progredir carga do threshold. Incluir treino em posição ortostática."
            ),
            "medicoes": [
                {"indicador_id": str(ind_spo2), "nome_indicador": "SpO2 em Repouso",
                 "valor_registrado": "92", "unidade": "%"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=4),
        },
    ]

    for ev in evolucoes:
        ev.setdefault("indicador_reavaliado", None)
        ev.setdefault("valor_atual", None)
        ev.setdefault("houve_progresso", None)
        ev.setdefault("condicao_meta", None)
        ev.setdefault("motivo_ajuste", None)
        ev.setdefault("proxima_revisao", None)
        await db.fato_evolucao.insert_one(ev)

    print(f"  ✅ {len(evolucoes)} Evoluções criadas")

    print("\n🚀 Seed finalizado com sucesso!")
    print(f"   {len(pacientes_data)} pacientes | {len(ids_pront)} prontuários | {len(metas)} metas | {len(evolucoes)} evoluções")
    print()
    print("   Credenciais (senha: ucb@1234):")
    print("   admin01   → Administrador Sistema")
    print("   docente01 → Profa. Ana Lima")
    print("   est01     → João Victor Rodrigues Pinto")
    print("   est02     → Maria Eduarda Santos")
    print()
    print("   Dashboard — dados de demonstração:")
    print("   📊 4 CIDs distintos | 4 áreas clínicas | 2 estagiários")
    print("   ⚠️  Alertas de risco: 2 prontuários com dor | 1 meta estagnada/atrasada")
    print("   ✅ Evoluções: 6 aprovadas | 4 pendentes | 1 devolvida")
    client.close()


if __name__ == "__main__":
    asyncio.run(rodar_seed())
