"""
Seed do ProntuSMART — popula uma visão padrão completa do sistema.

Coleções limpas:
- dim_usuario, dim_area, dim_indicador
- dim_paciente, fato_prontuario, fato_meta_smart
- fato_evolucao, fato_medicao, fato_relatorio

Coleção PRESERVADA:
- dim_cid (base oficial de 14k registros)

Cenário criado:
- 1 Administrador
- 2 Docentes (Profa. Ana Lima — Neurologia/Traumato; Prof. Carlos Mendes — Geriatria/Cardio)
- 2 Estagiários:
    • João Victor      → área Neurologia Adulto
    • Maria Eduarda    → área Geriatria
- 4 Pacientes em 4 áreas distintas, com triagem completa, avaliação funcional,
  metas SMART, evoluções e revisões cruzadas dos 2 docentes.
- 3 Relatórios de exemplo (1 rascunho, 1 aguardando docente, 1 finalizado).
"""
import asyncio
import hashlib
import json
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.dim_usuario import TipoPerfil
from src.models.dim_indicador import DirecaoMelhora
from src.models.dim_status import StatusMeta, StatusProntuario
from src.models.fato_relatorio import TipoRelatorio, StatusRelatorio


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


def _hash_doc(payload: dict) -> str:
    """SHA256 de um dicionário — usado para gerar hash de assinatura nas seeds."""
    base = {k: v for k, v in payload.items() if k not in ("assinatura_estagiario", "assinatura_docente", "_id", "criado_em", "atualizado_em")}
    raw  = json.dumps(base, default=str, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def rodar_seed():
    print("🌱 Iniciando seed do ProntuSMART...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # ── Limpa coleções — dim_cid PRESERVADA ─────────────────────────────────
    colecoes = [
        "dim_usuario", "dim_area", "dim_indicador",
        "dim_paciente", "fato_prontuario", "fato_meta_smart",
        "fato_evolucao", "fato_medicao", "fato_relatorio",
    ]
    for col in colecoes:
        await db[col].drop()
        print(f"  🗑️  Coleção '{col}' limpa")
    print("  ⚠️  dim_cid preservada (14k registros mantidos)")

    agora = datetime.now(timezone.utc)

    # ────────────────────────────────────────────────────────────────────────
    # 1. ÁREAS
    # ────────────────────────────────────────────────────────────────────────
    areas = [
        {"nome": "Saúde do Homem e da Mulher", "descricao": "Fisioterapia pélvica e saúde preventiva", "icone": "ph:person-simple-walk-bold", "cor": "rose",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Geriatria",                  "descricao": "Saúde do idoso e prevenção de quedas",     "icone": "ph:wheelchair-bold",         "cor": "amber",   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Neurologia Adulto",          "descricao": "Reabilitação neurofuncional para adultos", "icone": "ph:brain-bold",              "cor": "purple",  "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Neuropediatria",             "descricao": "Reabilitação neurofuncional pediátrica",   "icone": "ph:baby-bold",               "cor": "cyan",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Traumato-Ortopedia",         "descricao": "Reabilitação de fraturas e lesões",        "icone": "ph:bone-bold",               "cor": "blue",    "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Cardiorrespiratória",        "descricao": "Reabilitação cardíaca e pulmonar",         "icone": "ph:lungs-bold",              "cor": "emerald", "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for a in areas:
        await db.dim_area.insert_one(a)
    print(f"  ✅ {len(areas)} Áreas cadastradas")

    # ────────────────────────────────────────────────────────────────────────
    # 2. INDICADORES
    # ────────────────────────────────────────────────────────────────────────
    indicadores = [
        {"nome": "Escala Visual Analógica (EVA)", "unidade_medida": "pontos (0-10)", "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "descricao": "Intensidade da dor relatada pelo paciente.",          "areas_vinculadas": ["Todas"],                                                "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Escala de Berg",                "unidade_medida": "pontos (0-56)", "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Avalia equilíbrio funcional — ≤45 indica risco de queda.", "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                       "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Time Up and Go (TUG)",          "unidade_medida": "segundos",      "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "descricao": "Avalia mobilidade, equilíbrio e risco de quedas.",        "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                       "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Distância de Marcha",           "unidade_medida": "metros",        "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Distância percorrida com ou sem dispositivo auxiliar.",   "areas_vinculadas": ["Geriatria", "Neurologia Adulto", "Traumato-Ortopedia"], "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Tempo em Ortostatismo Estável", "unidade_medida": "segundos",      "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Tempo em pé sem perda de equilíbrio.",                    "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                       "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Força Muscular (Grau 0-5)",     "unidade_medida": "grau",          "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Graduação da força muscular por grupo muscular.",         "areas_vinculadas": ["Traumato-Ortopedia", "Neurologia Adulto"],              "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Amplitude de Movimento (ADM)",  "unidade_medida": "graus",         "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Amplitude articular em goniometria.",                    "areas_vinculadas": ["Traumato-Ortopedia"],                                   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "SpO2 em Repouso",               "unidade_medida": "%",             "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Saturação periférica de oxigênio.",                      "areas_vinculadas": ["Cardiorrespiratória"],                                  "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for indicador in indicadores:
        await db.dim_indicador.insert_one(indicador)
    print(f"  ✅ {len(indicadores)} Indicadores cadastrados")

    # ────────────────────────────────────────────────────────────────────────
    # 3. USUÁRIOS — 1 admin + 2 docentes + 2 estagiários
    # ────────────────────────────────────────────────────────────────────────
    senha_hash = get_password_hash("ucb@1234")
    usuarios = [
        # Administrador
        {"nome_completo": "Administrador Sistema", "matricula": "admin01", "email": "admin@ucb.br",
         "senha_hash": senha_hash, "perfil": TipoPerfil.ADMINISTRADOR, "area_atendimento": None,
         "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},

        # Docente 1 — Profa. Ana Lima (Neurologia + Traumato)
        {"nome_completo": "Profa. Ana Lima", "matricula": "doc01", "email": "ana.lima@ucb.br",
         "senha_hash": senha_hash, "perfil": TipoPerfil.DOCENTE, "area_atendimento": None,
         "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},

        # Docente 2 — Prof. Carlos Mendes (Geriatria + Cardio)
        {"nome_completo": "Prof. Carlos Mendes", "matricula": "doc02", "email": "carlos.mendes@ucb.br",
         "senha_hash": senha_hash, "perfil": TipoPerfil.DOCENTE, "area_atendimento": None,
         "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},

        # Estagiário 1 — João Victor (Neurologia Adulto)
        {"nome_completo": "João Victor Rodrigues Pinto", "matricula": "est01", "email": "joao.victor@ucb.br",
         "senha_hash": senha_hash, "perfil": TipoPerfil.ESTAGIARIO, "area_atendimento": "Neurologia Adulto",
         "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},

        # Estagiário 2 — Maria Eduarda (Geriatria)
        {"nome_completo": "Maria Eduarda Santos", "matricula": "est02", "email": "m.eduarda@ucb.br",
         "senha_hash": senha_hash, "perfil": TipoPerfil.ESTAGIARIO, "area_atendimento": "Geriatria",
         "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
    ]
    ids_u: dict = {}
    for u in usuarios:
        res = await db.dim_usuario.insert_one(u)
        ids_u[u["matricula"]] = res.inserted_id
    print(f"  ✅ {len(usuarios)} Usuários cadastrados")
    print(f"     • Docente Ana Lima → revisora de Neuro + Traumato")
    print(f"     • Docente Carlos Mendes → revisor de Geriatria + Cardio")
    print(f"     • Estagiário João Victor → área Neurologia Adulto")
    print(f"     • Estagiária Maria Eduarda → área Geriatria")

    docente_ana    = ids_u["doc01"]   # Profa. Ana Lima
    docente_carlos = ids_u["doc02"]   # Prof. Carlos Mendes
    est01_id       = ids_u["est01"]   # João Victor
    est02_id       = ids_u["est02"]   # Maria Eduarda

    # ────────────────────────────────────────────────────────────────────────
    # 4. PACIENTES
    # ────────────────────────────────────────────────────────────────────────
    pacientes_data = [
        # Paciente 1 — Neurologia Adulto (estagiário João Victor / docente Ana)
        {
            "nome_completo": "Carlos Alberto Ferreira", "cpf": "123.456.789-00",
            "data_nascimento": "1958-03-12", "sexo": "Masculino",
            "telefone_contato": "(61) 98765-4321", "email": "carlos.ferreira@email.com",
            "endereco_resumido": "QNM 38 Conjunto I, Ceilândia - DF",
            "area_atendimento_atual": "Neurologia Adulto",
            "queixa_principal": "Dificuldade para andar sozinho dentro de casa",
            "is_ativo": True, "criado_em": agora - timedelta(days=30), "atualizado_em": agora,
        },
        # Paciente 2 — Geriatria (estagiária Maria Eduarda / docente Carlos)
        {
            "nome_completo": "Maria das Graças Oliveira", "cpf": "234.567.890-11",
            "data_nascimento": "1945-07-22", "sexo": "Feminino",
            "telefone_contato": "(61) 91234-5678", "email": "mgraca@email.com",
            "endereco_resumido": "SQN 315 Bloco C, Asa Norte - DF",
            "area_atendimento_atual": "Geriatria",
            "queixa_principal": "Dor lombar crônica com dificuldade de deambulação",
            "is_ativo": True, "criado_em": agora - timedelta(days=45), "atualizado_em": agora,
        },
        # Paciente 3 — Traumato-Ortopedia (estagiário João Victor / docente Ana)
        {
            "nome_completo": "Roberto Lima da Silva", "cpf": "345.678.901-22",
            "data_nascimento": "1962-11-05", "sexo": "Masculino",
            "telefone_contato": "(61) 99876-5432", "email": "roberto.lima@email.com",
            "endereco_resumido": "QI 25 Conjunto 12, Guará - DF",
            "area_atendimento_atual": "Traumato-Ortopedia",
            "queixa_principal": "Limitação de movimentos e dor no quadril esquerdo pós-fratura",
            "is_ativo": True, "criado_em": agora - timedelta(days=20), "atualizado_em": agora,
        },
        # Paciente 4 — Cardiorrespiratória (estagiária Maria Eduarda / docente Carlos)
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

    # ────────────────────────────────────────────────────────────────────────
    # 5. CIDs
    # ────────────────────────────────────────────────────────────────────────
    cid1_id = await _get_cid(db, "I63.9", "Acidente vascular cerebral isquêmico, não especificado")
    cid2_id = await _get_cid(db, "M54.5", "Dor lombar")
    cid3_id = await _get_cid(db, "S72.0", "Fratura do colo do fêmur")
    cid4_id = await _get_cid(db, "J44.1", "Doença pulmonar obstrutiva crônica com exacerbação aguda")

    # ────────────────────────────────────────────────────────────────────────
    # 6. INDICADORES (busca IDs pelo nome)
    # ────────────────────────────────────────────────────────────────────────
    async def get_ind_id(nome):
        doc = await db.dim_indicador.find_one({"nome": nome})
        assert doc is not None, f"Indicador '{nome}' não encontrado!"
        return doc["_id"]

    ind_distancia = await get_ind_id("Distância de Marcha")
    ind_berg      = await get_ind_id("Escala de Berg")
    ind_tug       = await get_ind_id("Time Up and Go (TUG)")
    ind_adm       = await get_ind_id("Amplitude de Movimento (ADM)")
    ind_forca     = await get_ind_id("Força Muscular (Grau 0-5)")
    ind_spo2      = await get_ind_id("SpO2 em Repouso")

    # ────────────────────────────────────────────────────────────────────────
    # 7. PRONTUÁRIOS
    # NOTA: docente_id NÃO é mais setado no prontuário — o vínculo
    # docente↔paciente é feito por meio das revisões de evoluções.
    # ────────────────────────────────────────────────────────────────────────

    # Prontuário 1 — Carlos Alberto (Neurologia Adulto, est01)
    pront1 = {
        "paciente_id": str(pac1_id), "estagiario_id": str(est01_id),
        "docente_id":  None, "cid_id": str(cid1_id),
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
        "dor": False,
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

    # Prontuário 2 — Maria das Graças (Geriatria, est02) — alerta de dor
    pront2 = {
        "paciente_id": str(pac2_id), "estagiario_id": str(est02_id),
        "docente_id":  None, "cid_id": str(cid2_id),
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
        "dor": True,
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

    # Prontuário 3 — Roberto Lima (Traumato-Ortopedia, est01)
    pront3 = {
        "paciente_id": str(pac3_id), "estagiario_id": str(est01_id),
        "docente_id":  None, "cid_id": str(cid3_id),
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

    # Prontuário 4 — Sandra Costa (Cardiorrespiratória, est02)
    pront4 = {
        "paciente_id": str(pac4_id), "estagiario_id": str(est02_id),
        "docente_id":  None, "cid_id": str(cid4_id),
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

    # ────────────────────────────────────────────────────────────────────────
    # 8. METAS SMART
    # ────────────────────────────────────────────────────────────────────────
    metas = [
        # Pront1 — Carlos Alberto — Distância de Marcha
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
        # Pront1 — Carlos Alberto — Escala de Berg
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
        # Pront2 — Maria das Graças — TUG (atrasada)
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
            "data_limite": agora - timedelta(days=14),
            "data_reavaliacao": agora + timedelta(days=7),
            "status": StatusMeta.EM_ANDAMENTO, "progresso_percentual": 15.0,
            "historico_alteracoes": [], "criado_em": agora - timedelta(days=45), "atualizado_em": agora,
        },
        # Pront3 — Roberto Lima — ADM
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

    # ────────────────────────────────────────────────────────────────────────
    # 9. EVOLUÇÕES — REVISÕES CRUZADAS DOS 2 DOCENTES
    # Profa. Ana Lima  → revisora de Pront1 (Neuro) e Pront3 (Traumato)
    # Prof. Carlos Mendes → revisor de Pront2 (Geriatria) e Pront4 (Cardio)
    # ────────────────────────────────────────────────────────────────────────
    evolucoes = [
        # ── Pront1 Carlos Alberto (Neuro) — revisora: Ana ──────────────────
        {
            "prontuario_id": str(pront1_id), "autor_id": str(est01_id),
            "medicoes": [
                {"indicador_id": str(ind_distancia), "nome_indicador": "Distância de Marcha", "valor_registrado": "7", "unidade": "metros"},
                {"indicador_id": str(ind_berg),      "nome_indicador": "Escala de Berg",      "valor_registrado": "34", "unidade": "pontos (0-56)"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_ana),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=21),
        },
        {
            "prontuario_id": str(pront1_id), "autor_id": str(est01_id),
            "medicoes": [
                {"indicador_id": str(ind_distancia), "nome_indicador": "Distância de Marcha", "valor_registrado": "8.5", "unidade": "metros"},
                {"indicador_id": str(ind_berg),      "nome_indicador": "Escala de Berg",      "valor_registrado": "38",  "unidade": "pontos (0-56)"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_ana),
            "feedback_docente": "Excelente progressão. Continue documentando o tempo gasto em cada deslocamento.",
            "criado_em": agora - timedelta(days=10),
        },
        {
            "prontuario_id": str(pront1_id), "autor_id": str(est01_id),
            "medicoes": [
                {"indicador_id": str(ind_distancia), "nome_indicador": "Distância de Marcha", "valor_registrado": "10", "unidade": "metros"},
                {"indicador_id": str(ind_berg),      "nome_indicador": "Escala de Berg",      "valor_registrado": "42", "unidade": "pontos (0-56)"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=2),
        },

        # ── Pront3 Roberto Lima (Traumato) — revisora: Ana ─────────────────
        {
            "prontuario_id": str(pront3_id), "autor_id": str(est01_id),
            "medicoes": [
                {"indicador_id": str(ind_adm),   "nome_indicador": "Amplitude de Movimento (ADM)", "valor_registrado": "60", "unidade": "graus"},
                {"indicador_id": str(ind_forca), "nome_indicador": "Força Muscular (Grau 0-5)",    "valor_registrado": "3",  "unidade": "grau"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_ana),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=12),
        },
        {
            "prontuario_id": str(pront3_id), "autor_id": str(est01_id),
            "medicoes": [
                {"indicador_id": str(ind_adm),   "nome_indicador": "Amplitude de Movimento (ADM)", "valor_registrado": "75", "unidade": "graus"},
                {"indicador_id": str(ind_forca), "nome_indicador": "Força Muscular (Grau 0-5)",    "valor_registrado": "4",  "unidade": "grau"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=5),
        },

        # ── Pront2 Maria das Graças (Geriatria) — revisor: Carlos ──────────
        {
            "prontuario_id": str(pront2_id), "autor_id": str(est02_id),
            "medicoes": [
                {"indicador_id": str(ind_tug), "nome_indicador": "Time Up and Go (TUG)", "valor_registrado": "20", "unidade": "segundos"},
            ],
            "status": "Ajustes Solicitados",
            "docente_revisor_id": str(docente_carlos),
            "feedback_docente": (
                "Boa observação clínica. Inclua na próxima evolução a mensuração da EVA antes e após "
                "a sessão para acompanhar o efeito imediato das técnicas. Descreva também as técnicas "
                "analgésicas utilizadas (TENS, crioterapia, etc.)."
            ),
            "criado_em": agora - timedelta(days=30),
        },
        {
            "prontuario_id": str(pront2_id), "autor_id": str(est02_id),
            "medicoes": [
                {"indicador_id": str(ind_tug), "nome_indicador": "Time Up and Go (TUG)", "valor_registrado": "19.5", "unidade": "segundos"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_carlos),
            "feedback_docente": "Ótimo ajuste. Documentação muito mais consistente.",
            "criado_em": agora - timedelta(days=18),
        },
        {
            "prontuario_id": str(pront2_id), "autor_id": str(est02_id),
            "medicoes": [
                {"indicador_id": str(ind_tug), "nome_indicador": "Time Up and Go (TUG)", "valor_registrado": "18", "unidade": "segundos"},
            ],
            "status": "Pendente de Revisão",
            "docente_revisor_id": None,
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=3),
        },

        # ── Pront4 Sandra Costa (Cardio) — revisor: Carlos ─────────────────
        {
            "prontuario_id": str(pront4_id), "autor_id": str(est02_id),
            "medicoes": [
                {"indicador_id": str(ind_spo2), "nome_indicador": "SpO2 em Repouso", "valor_registrado": "91", "unidade": "%"},
            ],
            "status": "Aprovado e Assinado",
            "docente_revisor_id": str(docente_carlos),
            "feedback_docente": None,
            "criado_em": agora - timedelta(days=10),
        },
        {
            "prontuario_id": str(pront4_id), "autor_id": str(est02_id),
            "medicoes": [
                {"indicador_id": str(ind_spo2), "nome_indicador": "SpO2 em Repouso", "valor_registrado": "92", "unidade": "%"},
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

    # ────────────────────────────────────────────────────────────────────────
    # 10. RELATÓRIOS DE EXEMPLO
    # ────────────────────────────────────────────────────────────────────────

    # Relatório 1 — PADRÃO FINALIZADO
    # Pront1 Carlos Alberto (est01 João Victor) → docente Ana já assinou
    rel1_base = {
        "prontuario_id":  str(pront1_id), "paciente_id": str(pac1_id),
        "estagiario_id":  str(est01_id),  "docente_id":  str(docente_ana),
        "numero_relatorio": f"REL-{agora.year}-10001",
        "tipo":   TipoRelatorio.PADRAO,
        "status": StatusRelatorio.FINALIZADO,
        "diagnostico_clinico":          "Acidente vascular cerebral isquêmico",
        "queixa_principal":             "Dificuldade para andar sozinho dentro de casa",
        "diagnostico_fisioterapeutico": "Déficit de mobilidade funcional com prejuízo de marcha, transferências e equilíbrio",
        "objetivos_tratamento":         "Melhorar a marcha funcional, ganhar equilíbrio dinâmico, treinar transferências e segurança nas AVDs",
        "atividades_realizadas":        "Treino de marcha com andador, exercícios de equilíbrio em ortostatismo, fortalecimento de MMII e treino funcional para transferências",
        "observacoes_evolucao":         "Durante o tratamento foi possível observar ganho expressivo na distância de marcha (5m → 10m) e na pontuação da Escala de Berg (28 → 42 pontos). Equilíbrio dinâmico ainda em progressão.",
        "consideracoes_finais":         "Desde já, me coloco à disposição para maiores esclarecimentos sobre o quadro funcional e musculoesquelético do paciente.",
        "data_emissao": agora - timedelta(days=1),
        "criado_em":    agora - timedelta(days=2),
        "atualizado_em": agora - timedelta(days=1),
    }
    rel1_hash = _hash_doc(rel1_base)
    rel1_base["hash_integridade"] = rel1_hash
    rel1_base["assinatura_estagiario"] = {
        "usuario_id":      str(est01_id),
        "nome_completo":   "João Victor Rodrigues Pinto",
        "matricula":       "est01",
        "perfil":          "Estagiario",
        "data_assinatura": agora - timedelta(days=2),
        "hash_documento":  rel1_hash,
    }
    rel1_base["assinatura_docente"] = {
        "usuario_id":      str(docente_ana),
        "nome_completo":   "Profa. Ana Lima",
        "matricula":       "doc01",
        "perfil":          "Docente",
        "data_assinatura": agora - timedelta(days=1),
        "hash_documento":  rel1_hash,
    }
    await db.fato_relatorio.insert_one(rel1_base)

    # Relatório 2 — PADRÃO AGUARDANDO DOCENTE
    # Pront2 Maria das Graças (est02 Maria Eduarda) → estagiária assinou, docente Carlos pendente
    rel2_base = {
        "prontuario_id":  str(pront2_id), "paciente_id": str(pac2_id),
        "estagiario_id":  str(est02_id),  "docente_id":  str(docente_carlos),
        "numero_relatorio": f"REL-{agora.year}-10002",
        "tipo":   TipoRelatorio.PADRAO,
        "status": StatusRelatorio.AGUARDANDO_DOCENTE,
        "diagnostico_clinico":          "Lombalgia crônica com irradiação para membros inferiores",
        "queixa_principal":             "Dor lombar crônica com dificuldade de deambulação",
        "diagnostico_fisioterapeutico": "Síndrome dolorosa lombar com limitação funcional de marcha e mobilidade",
        "objetivos_tratamento":         "Reduzir intensidade da dor, melhorar tolerância à marcha e devolver autonomia para deslocamentos comunitários",
        "atividades_realizadas":        "Aplicação de TENS lombar, alongamentos da musculatura paravertebral, exercícios de estabilização lombar e treino de marcha com bengala",
        "observacoes_evolucao":         "Houve redução da dor (EVA 7/10 → 6/10) e melhora discreta no TUG (22s → 18s). Paciente recuperou autonomia para ir à padaria do bairro durante o tratamento.",
        "consideracoes_finais":         "",
        "criado_em":     agora - timedelta(hours=12),
        "atualizado_em": agora - timedelta(hours=8),
    }
    rel2_hash = _hash_doc(rel2_base)
    rel2_base["assinatura_estagiario"] = {
        "usuario_id":      str(est02_id),
        "nome_completo":   "Maria Eduarda Santos",
        "matricula":       "est02",
        "perfil":          "Estagiario",
        "data_assinatura": agora - timedelta(hours=8),
        "hash_documento":  rel2_hash,
    }
    await db.fato_relatorio.insert_one(rel2_base)

    # Relatório 3 — COMPLETO RASCUNHO
    # Pront3 Roberto Lima — estagiário ainda não assinou
    rel3_base = {
        "prontuario_id":  str(pront3_id), "paciente_id": str(pac3_id),
        "estagiario_id":  str(est01_id),  "docente_id":  None,
        "numero_relatorio": f"REL-{agora.year}-10003",
        "tipo":   TipoRelatorio.COMPLETO,
        "status": StatusRelatorio.RASCUNHO,
        "diagnostico_clinico":          "Fratura do colo do fêmur esquerdo — pós-artroplastia total de quadril",
        "queixa_principal":             "Limitação de movimentos e dor no quadril esquerdo pós-operatória",
        "diagnostico_fisioterapeutico": "Limitação de ADM de quadril e déficit de força em MMII",
        "objetivos_tratamento":         "Recuperar amplitude de movimento de flexão de quadril, ganhar força em MMII e devolver marcha segura",
        "atividades_realizadas":        "Mobilização articular passiva e ativa-assistida, fortalecimento isométrico, exercícios em cadeia cinética fechada e treino de marcha com muletas",
        "observacoes_evolucao":         "Boa evolução. ADM passou de 45° para 75° de flexão. Força muscular passou de grau 3 para grau 4.",
        "consideracoes_finais":         "",
        "criado_em":     agora - timedelta(hours=4),
        "atualizado_em": agora - timedelta(hours=4),
    }
    await db.fato_relatorio.insert_one(rel3_base)

    print(f"  ✅ 3 Relatórios de exemplo criados")
    print(f"     • REL-{agora.year}-10001 → Padrão FINALIZADO (Carlos Alberto)")
    print(f"     • REL-{agora.year}-10002 → Padrão AGUARDANDO DOCENTE (Maria das Graças)")
    print(f"     • REL-{agora.year}-10003 → Completo RASCUNHO (Roberto Lima)")

    # ────────────────────────────────────────────────────────────────────────
    # FIM
    # ────────────────────────────────────────────────────────────────────────
    print("\n🚀 Seed finalizado com sucesso!")
    print(f"   {len(pacientes_data)} pacientes | {len(ids_pront)} prontuários | {len(metas)} metas | {len(evolucoes)} evoluções | 3 relatórios")
    print()
    print("   Credenciais (senha: ucb@1234):")
    print("   admin01  → Administrador Sistema")
    print("   doc01    → Profa. Ana Lima       (revisora Neuro + Traumato)")
    print("   doc02    → Prof. Carlos Mendes   (revisor Geriatria + Cardio)")
    print("   est01    → João Victor (Neurologia Adulto)")
    print("   est02    → Maria Eduarda (Geriatria)")
    print()
    print("   Dashboard — dados de demonstração:")
    print("   📊 4 CIDs distintos | 4 áreas clínicas | 2 estagiários | 2 docentes")
    print("   ⚠️  Alertas de risco: 2 prontuários com dor | 1 meta estagnada/atrasada")
    print("   ✅ Evoluções: 6 aprovadas | 4 pendentes | 1 devolvida")
    print("   📄 Relatórios: 1 finalizado | 1 aguardando docente | 1 rascunho")
    client.close()


if __name__ == "__main__":
    asyncio.run(rodar_seed())
