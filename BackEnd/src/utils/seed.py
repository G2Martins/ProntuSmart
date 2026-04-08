import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.dim_usuario import TipoPerfil
from src.models.dim_indicador import DirecaoMelhora
from src.models.dim_status import StatusMeta, StatusProntuario

async def rodar_seed():
    print("🌱 Iniciando seed do ProntuSMART...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # ── Limpa coleções — dim_cid PRESERVADA (14k registros) ──
    colecoes = [
        "dim_usuario", "dim_area", "dim_indicador",
        "dim_paciente", "fato_prontuario", "fato_meta_smart",
        "fato_evolucao", "fato_medicao"
    ]
    for col in colecoes:
        await db[col].drop()
        print(f"  🗑️  Coleção '{col}' limpa")
    print("  ⚠️  dim_cid preservada (14k registros mantidos)")

    agora = datetime.now(timezone.utc)

    # ── 1. ÁREAS ─────────────────────────────────────────────
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

    # ── 2. INDICADORES ───────────────────────────────────────
    indicadores = [
        {"nome": "Escala Visual Analógica (EVA)",     "unidade_medida": "pontos (0-10)",   "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "descricao": "Intensidade da dor relatada pelo paciente.",                    "areas_vinculadas": ["Todas"],                                            "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Escala de Berg",                    "unidade_medida": "pontos (0-56)",   "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Avalia equilíbrio funcional — ≤45 indica risco de queda.",     "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Time Up and Go (TUG)",              "unidade_medida": "segundos",        "direcao_melhora": DirecaoMelhora.MENOR_MELHOR, "descricao": "Avalia mobilidade, equilíbrio e risco de quedas.",             "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Distância de Marcha",               "unidade_medida": "metros",          "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Distância percorrida com ou sem dispositivo auxiliar.",        "areas_vinculadas": ["Geriatria", "Neurologia Adulto", "Traumato-Ortopedia"], "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Tempo em Ortostatismo Estável",     "unidade_medida": "segundos",        "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Tempo em pé sem perda de equilíbrio.",                        "areas_vinculadas": ["Geriatria", "Neurologia Adulto"],                   "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Força Muscular (Grau 0-5)",         "unidade_medida": "grau",            "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Graduação da força muscular por grupo muscular.",              "areas_vinculadas": ["Traumato-Ortopedia", "Neurologia Adulto"],          "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "Amplitude de Movimento (ADM)",      "unidade_medida": "graus",           "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Amplitude articular em goniometria.",                         "areas_vinculadas": ["Traumato-Ortopedia"],                               "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
        {"nome": "SpO2 em Repouso",                   "unidade_medida": "%",               "direcao_melhora": DirecaoMelhora.MAIOR_MELHOR, "descricao": "Saturação periférica de oxigênio.",                           "areas_vinculadas": ["Cardiorrespiratória"],                              "is_ativo": True, "criado_em": agora, "atualizado_em": agora},
    ]
    for ind in indicadores:
        await db.dim_indicador.insert_one(ind)
    print(f"  ✅ {len(indicadores)} Indicadores cadastrados")

    # ── 3. USUÁRIOS ──────────────────────────────────────────
    senha_hash = get_password_hash("ucb@1234")
    usuarios = [
        {"nome_completo": "Administrador Sistema",       "matricula": "admin01",    "email": "admin@ucb.br",          "senha_hash": senha_hash, "perfil": TipoPerfil.ADMINISTRADOR, "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
        {"nome_completo": "Profa. Ana Lima",             "matricula": "docente01",  "email": "ana.lima@ucb.br",       "senha_hash": senha_hash, "perfil": TipoPerfil.DOCENTE,       "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
        {"nome_completo": "João Victor Rodrigues Pinto", "matricula": "est01",      "email": "joao.victor@ucb.br",    "senha_hash": senha_hash, "perfil": TipoPerfil.ESTAGIARIO,   "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
        {"nome_completo": "Maria Eduarda Santos",        "matricula": "est02",      "email": "m.eduarda@ucb.br",      "senha_hash": senha_hash, "perfil": TipoPerfil.ESTAGIARIO,   "is_ativo": True, "precisa_trocar_senha": False, "criado_em": agora, "atualizado_em": agora},
    ]
    ids_usuarios: dict = {}
    for u in usuarios:
        res = await db.dim_usuario.insert_one(u)
        ids_usuarios[u["matricula"]] = res.inserted_id
    print(f"  ✅ {len(usuarios)} Usuários cadastrados")

    docente_id    = ids_usuarios["docente01"]
    estagiario_id = ids_usuarios["est01"]

    # ── 4. PACIENTE EXEMPLO ───────────────────────────────────
    paciente_exemplo = {
        "nome_completo":          "Carlos Alberto Ferreira",
        "cpf":                    "123.456.789-00",
        "data_nascimento":        "1958-03-12",
        "sexo":                   "Masculino",
        "telefone_contato":       "(61) 98765-4321",
        "email":                  "carlos.ferreira@email.com",
        "endereco_resumido":      "QNM 38 Conjunto I, Ceilândia - DF",
        "area_atendimento_atual": "Neurologia Adulto",
        "queixa_principal":       "Dificuldade para andar sozinho dentro de casa",
        "is_ativo":               True,
        "criado_em":              agora,
        "atualizado_em":          agora,
    }
    res_pac   = await db.dim_paciente.insert_one(paciente_exemplo)
    paciente_id = res_pac.inserted_id
    print("  ✅ Paciente exemplo cadastrado")

    # ── 5. CID — busca o I63.9 já existente na base dos 14k ──
    cid_doc = await db.dim_cid.find_one({"codigo": "I63.9"})
    if cid_doc is None:
        # Se por alguma razão não existir, insere
        res_cid = await db.dim_cid.insert_one({
            "codigo":    "I63.9",
            "descricao": "Acidente vascular cerebral isquêmico, não especificado",
            "is_ativo":  True,
            "criado_em": agora,
            "atualizado_em": agora,
        })
        cid_id = res_cid.inserted_id
        print("  ⚠️  CID I63.9 não encontrado na base — inserido manualmente")
    else:
        cid_id = cid_doc["_id"]
        print("  ✅ CID I63.9 encontrado na base existente")

    # ── 6. PRONTUÁRIO EXEMPLO ─────────────────────────────────
    prontuario_exemplo = {
        "paciente_id":    str(paciente_id),
        "estagiario_id":  str(estagiario_id),
        "docente_id":     str(docente_id),
        "cid_id":         str(cid_id),
        "area_atendimento":   "Neurologia Adulto",
        "numero_prontuario":  f"UCB-{datetime.now().year}-00001",
        "status":             StatusProntuario.ATIVO,
        "total_sessoes":      1,
        "data_ultima_evolucao": agora - timedelta(days=7),
        # Tela 1
        "diagnostico_medico":            "Acidente vascular cerebral isquêmico",
        "diagnostico_fisioterapeutico":  "Déficit de mobilidade funcional com prejuízo de marcha, transferências e equilíbrio",
        "queixa_principal":              "Dificuldade para andar sozinho dentro de casa",
        "objetivo_paciente":             "Conseguir ir sozinho ao banheiro",
        "tempo_evolucao":                "3 meses",
        "comorbidades":                  "Hipertensão arterial sistêmica e diabetes mellitus tipo 2",
        "medicamentos":                  "Losartana, metformina, AAS",
        "dispositivo_auxiliar":          "Andador",
        "barreiras_ambientais":          "Casa com corredor estreito e banheiro sem barra de apoio",
        # Tela 2
        "sedestacao":         "Independente",
        "ortostatismo":       "Supervisão",
        "transferencias":     "Ajuda parcial",
        "realiza_marcha":     True,
        "marcha_dispositivo": True,
        "distancia_tolerada": "5 metros",
        "funcao_mmss":        "Parcialmente comprometida",
        "funcao_mmii":        "Parcialmente comprometida",
        "equilibrio":         "Alterado",
        "risco_queda":        "Alto",
        "dor":                False,
        "fadiga_funcional":   True,
        "compreende_comandos":    True,
        "comunicacao_preservada": True,
        "avd_banho":       "AP",
        "avd_vestir":      "AP",
        "avd_higiene":     "AP",
        "avd_locomocao":   "D",
        "avd_alimentacao": "I",
        "avd_banheiro":    "AP",
        "atividade_mais_impactada": "Locomoção dentro de casa",
        "principal_limitacao":     "Não consegue caminhar com segurança sem auxílio",
        "teste_escala_principal":  "Escala de Berg",
        "valor_teste_inicial":     "28 pontos",
        # Tela 3
        "problema_funcional_prioritario": "Déficit de marcha com risco aumentado de queda",
        "atividade_comprometida":         "Locomoção domiciliar",
        "impacto_independencia":          "Dependência parcial para deslocamento e insegurança ao realizar transferências",
        "prioridade_terapeutica":         "Melhorar marcha funcional e segurança nas transferências",
        "criado_em":     agora - timedelta(days=14),
        "atualizado_em": agora,
    }
    res_pront   = await db.fato_prontuario.insert_one(prontuario_exemplo)
    prontuario_id = res_pront.inserted_id
    print(f"  ✅ Prontuário exemplo criado: UCB-{datetime.now().year}-00001")

    # ── 7. INDICADORES para as metas (busca pelo nome) ───────
    ind_distancia = await db.dim_indicador.find_one({"nome": "Distância de Marcha"})
    ind_berg      = await db.dim_indicador.find_one({"nome": "Escala de Berg"})

    # Garante que foram encontrados antes de subscrever
    assert ind_distancia is not None, "Indicador 'Distância de Marcha' não encontrado!"
    assert ind_berg      is not None, "Indicador 'Escala de Berg' não encontrado!"

    # ── 8. METAS SMART EXEMPLO ───────────────────────────────
    meta1 = {
        "prontuario_id":       str(prontuario_id),
        "indicador_id":        str(ind_distancia["_id"]),
        "estagiario_id":       str(estagiario_id),
        "problema_relacionado":    "Déficit de marcha",
        "especifico":              "Melhorar a capacidade de marcha em ambiente domiciliar",
        "criterio_mensuravel":     "Caminhar 10 metros",
        "valor_inicial":           5.0,
        "valor_alvo":              10.0,
        "condicao_execucao":       "Com andador e supervisão",
        "alcancavel":              "Paciente apresenta musculatura preservada com potencial de ganho funcional",
        "relevante":               "Permitir deslocamento até o banheiro com mais independência",
        "data_limite":             agora + timedelta(days=28),
        "data_reavaliacao":        agora + timedelta(days=28),
        "status":                  StatusMeta.EM_ANDAMENTO,
        "progresso_percentual":    0.0,
        "historico_alteracoes":    [],
        "criado_em":               agora - timedelta(days=14),
        "atualizado_em":           agora,
    }
    meta2 = {
        "prontuario_id":       str(prontuario_id),
        "indicador_id":        str(ind_berg["_id"]),
        "estagiario_id":       str(estagiario_id),
        "problema_relacionado":    "Déficit de equilíbrio",
        "especifico":              "Melhorar equilíbrio em ortostatismo",
        "criterio_mensuravel":     "Permanecer 30 segundos em pé sem perda de equilíbrio",
        "valor_inicial":           8.0,
        "valor_alvo":              30.0,
        "condicao_execucao":       "Com supervisão, sem apoio manual constante",
        "alcancavel":              "Avaliação indica potencial de ganho de equilíbrio com treino específico",
        "relevante":               "Aumentar segurança para transferências e higiene pessoal",
        "data_limite":             agora + timedelta(days=28),
        "data_reavaliacao":        agora + timedelta(days=28),
        "status":                  StatusMeta.EM_ANDAMENTO,
        "progresso_percentual":    0.0,
        "historico_alteracoes":    [],
        "criado_em":               agora - timedelta(days=14),
        "atualizado_em":           agora,
    }
    await db.fato_meta_smart.insert_many([meta1, meta2])
    print("  ✅ 2 Metas SMART exemplo criadas")

    # ── 9. EVOLUÇÃO EXEMPLO ───────────────────────────────────
    evolucao_exemplo = {
        "prontuario_id": str(prontuario_id),
        "autor_id":      str(estagiario_id),
        "texto_clinico": (
            "S - Paciente relata melhora leve na disposição para caminhar, "
            "porém ainda sente insegurança ao realizar o percurso sem supervisão.\n"
            "O - Marcha realizada com andador, percorrendo 8 metros sem pausas. "
            "Controle postural melhorado em relação à sessão anterior.\n"
            "A - Evolução positiva observada. Meta de 10m com prazo mantido.\n"
            "P - Manter treino de marcha com andador, progredir para 10m "
            "e iniciar treino de equilíbrio em ortostatismo."
        ),
        "medicoes": [
            {"indicador_id": str(ind_distancia["_id"]), "nome_indicador": "Distância de Marcha",  "valor_registrado": "8",  "unidade": "metros"},
            {"indicador_id": str(ind_berg["_id"]),      "nome_indicador": "Escala de Berg",        "valor_registrado": "32", "unidade": "pontos (0-56)"},
        ],
        "indicador_reavaliado": "Distância de Marcha",
        "valor_atual":          "8 metros",
        "houve_progresso":      "Sim",
        "condicao_meta":        "Mantida",
        "motivo_ajuste":        None,
        "proxima_revisao":      agora + timedelta(days=14),
        "status":               "Pendente de Revisão",
        "docente_revisor_id":   None,
        "feedback_docente":     None,
        "criado_em":            agora - timedelta(days=7),
    }
    await db.fato_evolucao.insert_one(evolucao_exemplo)
    print("  ✅ Evolução exemplo criada")

    print("\n🚀 Seed finalizado com sucesso!")
    print("   admin01 / ucb@1234   → Administrador")
    print("   docente01 / ucb@1234 → Docente (Profa. Ana Lima)")
    print("   est01 / ucb@1234     → Estagiário (João Victor)")
    print("   est02 / ucb@1234     → Estagiário (Maria Eduarda)")
    client.close()

if __name__ == "__main__":
    asyncio.run(rodar_seed())