"""
Geração de PDFs de Relatórios Fisioterapêuticos.

Dois formatos:
- PADRÃO  → Modelo institucional UCB (uma página, com marca d'água oficial e
            assinaturas digitais ao final).
- COMPLETO → Snapshot técnico de todos os dados registrados (triagem,
             avaliação funcional, síntese, evoluções, metas, indicadores).
"""
from io import BytesIO
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from pypdf import PdfReader, PdfWriter

# Caminho absoluto para o template da marca d'água (resolvido a partir deste arquivo)
ASSETS_DIR    = Path(__file__).resolve().parent.parent / "assets" / "templates"
MARCA_DAGUA   = ASSETS_DIR / "marca_dagua.pdf"

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


# ═══════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════

def _calcular_idade(data_nascimento: Optional[str]) -> int:
    if not data_nascimento:
        return 0
    try:
        nasc = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    except ValueError:
        return 0
    hoje = date.today()
    return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))


def _data_extenso(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.now()
    return f"Brasília/DF, {dt.day:02d} de {MESES_PT[dt.month - 1]} de {dt.year}"


def _genero_extenso(sexo: Optional[str]) -> str:
    if not sexo:
        return "indefinido"
    return "feminino" if sexo.lower().startswith("f") else "masculino"


def _aplicar_marca_dagua(pdf_buffer: BytesIO) -> BytesIO:
    """Mescla o PDF de conteúdo com o template da marca d'água UCB.

    Se o template não existir, retorna o PDF original (graceful fallback).
    """
    if not MARCA_DAGUA.exists():
        pdf_buffer.seek(0)
        return pdf_buffer

    try:
        conteudo = PdfReader(pdf_buffer)
        marca    = PdfReader(str(MARCA_DAGUA))
        marca_pg = marca.pages[0]

        writer = PdfWriter()
        for pagina in conteudo.pages:
            # merge_page sobrepõe a marca d'água ABAIXO do conteúdo
            nova_pg = pagina
            nova_pg.merge_page(marca_pg, over=False)
            writer.add_page(nova_pg)

        out = BytesIO()
        writer.write(out)
        out.seek(0)
        return out
    except Exception:
        pdf_buffer.seek(0)
        return pdf_buffer


def _estilos_padrao():
    base = getSampleStyleSheet()
    return {
        "cabecalho": ParagraphStyle(
            "Cabecalho", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=11, alignment=TA_LEFT,
            textColor=black, spaceAfter=2,
        ),
        "titulo": ParagraphStyle(
            "Titulo", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER,
            textColor=black, spaceBefore=12, spaceAfter=14,
        ),
        "corpo": ParagraphStyle(
            "Corpo", parent=base["Normal"],
            fontName="Helvetica", fontSize=11, alignment=TA_JUSTIFY,
            leading=16, firstLineIndent=1.25 * cm, spaceAfter=10,
        ),
        "rodape": ParagraphStyle(
            "Rodape", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, alignment=TA_RIGHT,
            spaceBefore=24,
        ),
        "assinatura": ParagraphStyle(
            "Assinatura", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, alignment=TA_CENTER, leading=11,
        ),
        "secao": ParagraphStyle(
            "Secao", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=11, alignment=TA_LEFT,
            textColor=HexColor("#1e40af"), spaceBefore=14, spaceAfter=6,
            borderPadding=4,
        ),
        "label": ParagraphStyle(
            "Label", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9, textColor=HexColor("#6b7280"),
        ),
        "valor": ParagraphStyle(
            "Valor", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=13, alignment=TA_LEFT,
        ),
    }


def _bloco_assinaturas(relatorio: dict, estilos) -> list:
    """Tabela de assinaturas (estagiário | docente)."""
    assin_est  = relatorio.get("assinatura_estagiario") or {}
    assin_doc  = relatorio.get("assinatura_docente")    or {}

    def _bloco(rotulo: str, dados: dict) -> list:
        if not dados:
            return [
                Paragraph("____________________________", estilos["assinatura"]),
                Paragraph(f"<b>{rotulo}</b>", estilos["assinatura"]),
                Paragraph("<i>(não assinado)</i>", estilos["assinatura"]),
            ]
        data = dados.get("data_assinatura")
        if isinstance(data, str):
            try:
                data = datetime.fromisoformat(data.replace("Z", "+00:00"))
            except Exception:
                data = None
        data_txt = data.strftime("%d/%m/%Y · %H:%M") if isinstance(data, datetime) else "—"
        nome     = dados.get("nome_completo", "—")
        matricula = dados.get("matricula", "—")
        hash_doc  = (dados.get("hash_documento") or "")[:16]
        return [
            Paragraph("<b><font color='#16a34a'>✓ Assinado digitalmente</font></b>", estilos["assinatura"]),
            Paragraph(f"<b>{nome}</b>", estilos["assinatura"]),
            Paragraph(f"{rotulo} · Mat. {matricula}", estilos["assinatura"]),
            Paragraph(f"<font size='7' color='#6b7280'>{data_txt}<br/>SHA256: {hash_doc}…</font>", estilos["assinatura"]),
        ]

    col_est = _bloco("Estagiário", assin_est)
    col_doc = _bloco("Fisioterapeuta Supervisor", assin_doc)

    # Constroi tabela 1×2 onde cada célula tem o stack de Paragraphs
    tabela = Table([[col_est, col_doc]], colWidths=[8 * cm, 8 * cm])
    tabela.setStyle(TableStyle([
        ("VALIGN",   (0, 0), (-1, -1), "TOP"),
        ("ALIGN",    (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
    ]))
    return [Spacer(1, 24), tabela]


# ═══════════════════════════════════════════════════════════════════════
#  RELATÓRIO PADRÃO (modelo UCB)
# ═══════════════════════════════════════════════════════════════════════

def gerar_pdf_padrao(
    relatorio:  dict,
    paciente:   dict,
    prontuario: dict,
) -> bytes:
    """Gera o PDF do relatório no padrão institucional UCB."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=4.0 * cm, bottomMargin=4.0 * cm,
        title=f"Relatório {relatorio.get('numero_relatorio', '')}",
        author="ProntuSMART · UCB",
    )
    styles = _estilos_padrao()
    story = []

    # ── Cabeçalho institucional ──────────────────────────────
    story.append(Paragraph("UNIVERSIDADE CATÓLICA DE BRASÍLIA - UCB", styles["cabecalho"]))
    story.append(Paragraph("CURSO DE FISIOTERAPIA",                  styles["cabecalho"]))
    story.append(Paragraph("ESTÁGIO SUPERVISIONADO EM FISIOTERAPIA", styles["cabecalho"]))
    story.append(Paragraph("RELATÓRIO FISIOTERAPÊUTICO",             styles["titulo"]))

    # ── Apresentação do paciente ─────────────────────────────
    nome   = paciente.get("nome_completo", "—")
    sexo   = _genero_extenso(paciente.get("sexo"))
    idade  = _calcular_idade(paciente.get("data_nascimento"))
    diag_med = relatorio.get("diagnostico_clinico") or prontuario.get("diagnostico_medico") or "—"
    queixa   = relatorio.get("queixa_principal")    or prontuario.get("queixa_principal")  or "—"

    apresentacao = (
        f"Paciente <b>{nome}</b>, sexo {sexo}, {idade} anos, "
        f"com o diagnóstico clínico de {diag_med}. "
        f"A sua queixa principal na avaliação fisioterapêutica foi: "
        f"&ldquo;{queixa}&rdquo;."
    )
    story.append(Paragraph(apresentacao, styles["corpo"]))

    # ── Diagnóstico fisioterapêutico ────────────────────────
    diag_fisio = relatorio.get("diagnostico_fisioterapeutico") or prontuario.get("diagnostico_fisioterapeutico") or "—"
    story.append(Paragraph(
        f"Na avaliação foi observado que o(a) paciente apresenta o seguinte "
        f"diagnóstico fisioterapêutico: {diag_fisio}.",
        styles["corpo"]
    ))

    # ── Objetivos do tratamento ─────────────────────────────
    objetivos = relatorio.get("objetivos_tratamento") or "—"
    story.append(Paragraph(
        f"Os objetivos do tratamento foram: {objetivos}.",
        styles["corpo"]
    ))

    # ── Atividades realizadas + observações de evolução ─────
    atividades = relatorio.get("atividades_realizadas") or "—"
    observacoes = relatorio.get("observacoes_evolucao") or ""
    texto_atv = f"As principais atividades adotadas na fisioterapia consistiam em: {atividades}."
    if observacoes:
        texto_atv += f" {observacoes}"
    story.append(Paragraph(texto_atv, styles["corpo"]))

    # ── Considerações finais ────────────────────────────────
    consideracoes = relatorio.get("consideracoes_finais") or (
        "Desde já, me coloco à disposição para maiores esclarecimentos sobre o "
        "quadro funcional e musculoesquelético do(a) paciente."
    )
    story.append(Paragraph(consideracoes, styles["corpo"]))
    story.append(Paragraph("Atenciosamente,", styles["corpo"]))

    # ── Bloco de assinaturas digitais ────────────────────────
    story += _bloco_assinaturas(relatorio, styles)

    # ── Data de emissão ─────────────────────────────────────
    data_emissao = relatorio.get("data_emissao")
    if isinstance(data_emissao, str):
        try:
            data_emissao = datetime.fromisoformat(data_emissao.replace("Z", "+00:00"))
        except Exception:
            data_emissao = None
    story.append(Paragraph(_data_extenso(data_emissao if isinstance(data_emissao, datetime) else None), styles["rodape"]))

    doc.build(story)

    # Mescla com a marca d'água oficial
    final = _aplicar_marca_dagua(buffer)
    return final.getvalue()


# ═══════════════════════════════════════════════════════════════════════
#  RELATÓRIO COMPLETO (snapshot técnico)
# ═══════════════════════════════════════════════════════════════════════

def _kv_table(linhas: list[tuple[str, str]], col_label_width=4.5 * cm) -> Table:
    """Tabela compacta de chave/valor para o relatório completo."""
    data = []
    for label, valor in linhas:
        data.append([
            Paragraph(f"<b>{label}</b>", ParagraphStyle("k", fontName="Helvetica-Bold", fontSize=8, textColor=HexColor("#6b7280"))),
            Paragraph(valor or "—", ParagraphStyle("v", fontName="Helvetica", fontSize=9, leading=12)),
        ])
    t = Table(data, colWidths=[col_label_width, None])
    t.setStyle(TableStyle([
        ("VALIGN",  (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, HexColor("#e5e7eb")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    return t


def gerar_pdf_completo(
    relatorio:  dict,
    paciente:   dict,
    prontuario: dict,
    evolucoes:  list[dict],
    metas:      list[dict],
    docentes_revisores: list[dict] | None = None,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Relatório Completo {relatorio.get('numero_relatorio', '')}",
        author="ProntuSMART · UCB",
    )
    styles = _estilos_padrao()
    story = []

    # ── Cabeçalho ───────────────────────────────────────────
    story.append(Paragraph("RELATÓRIO CLÍNICO COMPLETO", styles["titulo"]))
    story.append(Paragraph(
        f"<font color='#6b7280' size='9'>Prontuário {prontuario.get('numero_prontuario','—')} · "
        f"Relatório {relatorio.get('numero_relatorio','—')} · "
        f"Emitido em {_data_extenso()}</font>",
        ParagraphStyle("sub", alignment=TA_CENTER, fontSize=9, spaceAfter=12)
    ))

    # ── Identificação ───────────────────────────────────────
    story.append(Paragraph("Identificação do Paciente", styles["secao"]))
    story.append(_kv_table([
        ("Nome completo",     paciente.get("nome_completo", "—")),
        ("CPF",               paciente.get("cpf", "—")),
        ("Data de nascimento",paciente.get("data_nascimento", "—")),
        ("Idade",             f"{_calcular_idade(paciente.get('data_nascimento'))} anos"),
        ("Sexo",              paciente.get("sexo", "—")),
        ("Telefone",          paciente.get("telefone_contato", "—")),
        ("E-mail",            paciente.get("email") or "—"),
        ("Endereço",          paciente.get("endereco_resumido") or "—"),
    ]))

    # ── Triagem (Tela 1) ────────────────────────────────────
    story.append(Paragraph("Triagem & Dados Iniciais", styles["secao"]))
    story.append(_kv_table([
        ("Diagnóstico médico",       prontuario.get("diagnostico_medico")),
        ("Diagnóstico fisioterapêutico", prontuario.get("diagnostico_fisioterapeutico")),
        ("Queixa principal",         prontuario.get("queixa_principal")),
        ("Objetivo do paciente",     prontuario.get("objetivo_paciente")),
        ("Tempo de evolução",        prontuario.get("tempo_evolucao")),
        ("Comorbidades",             prontuario.get("comorbidades")),
        ("Medicamentos em uso",      prontuario.get("medicamentos")),
        ("Dispositivo auxiliar",     prontuario.get("dispositivo_auxiliar")),
        ("Barreiras ambientais",     prontuario.get("barreiras_ambientais")),
    ]))

    # ── Avaliação Funcional (Tela 2) ────────────────────────
    story.append(Paragraph("Avaliação Funcional", styles["secao"]))
    def _bool(v): return "Sim" if v is True else ("Não" if v is False else "—")
    story.append(_kv_table([
        ("Sedestação",     prontuario.get("sedestacao")),
        ("Ortostatismo",   prontuario.get("ortostatismo")),
        ("Transferências", prontuario.get("transferencias")),
        ("Realiza marcha", _bool(prontuario.get("realiza_marcha"))),
        ("Usa dispositivo (marcha)", _bool(prontuario.get("marcha_dispositivo"))),
        ("Distância tolerada",       prontuario.get("distancia_tolerada")),
        ("Função MMSS",  prontuario.get("funcao_mmss")),
        ("Função MMII",  prontuario.get("funcao_mmii")),
        ("Equilíbrio",   prontuario.get("equilibrio")),
        ("Risco de queda", prontuario.get("risco_queda")),
        ("Apresenta dor", _bool(prontuario.get("dor"))),
        ("Intensidade/local da dor", prontuario.get("dor_intensidade_local")),
        ("Fadiga funcional", _bool(prontuario.get("fadiga_funcional"))),
        ("Compreende comandos", _bool(prontuario.get("compreende_comandos"))),
        ("Comunicação preservada", _bool(prontuario.get("comunicacao_preservada"))),
        ("AVD — Banho",       prontuario.get("avd_banho")),
        ("AVD — Vestir",      prontuario.get("avd_vestir")),
        ("AVD — Higiene",     prontuario.get("avd_higiene")),
        ("AVD — Locomoção",   prontuario.get("avd_locomocao")),
        ("AVD — Alimentação", prontuario.get("avd_alimentacao")),
        ("AVD — Banheiro",    prontuario.get("avd_banheiro")),
    ]))

    # ── Síntese (Tela 3) ────────────────────────────────────
    story.append(Paragraph("Síntese Fisioterapêutica", styles["secao"]))
    story.append(_kv_table([
        ("Problema funcional prioritário", prontuario.get("problema_funcional_prioritario")),
        ("Atividade comprometida",         prontuario.get("atividade_comprometida")),
        ("Impacto na independência",       prontuario.get("impacto_independencia")),
        ("Prioridade terapêutica",         prontuario.get("prioridade_terapeutica")),
    ]))

    # ── Metas SMART ─────────────────────────────────────────
    story.append(Paragraph(f"Metas SMART ({len(metas)})", styles["secao"]))
    if not metas:
        story.append(Paragraph("Nenhuma meta cadastrada.", styles["valor"]))
    else:
        for i, m in enumerate(metas, 1):
            data_lim = m.get("data_limite")
            if isinstance(data_lim, datetime):
                data_lim_txt = data_lim.strftime("%d/%m/%Y")
            else:
                data_lim_txt = str(data_lim)[:10] if data_lim else "—"
            story.append(_kv_table([
                (f"Meta #{i} — {m.get('status','—')}", m.get("especifico", "—")),
                ("Critério mensurável", m.get("criterio_mensuravel")),
                ("Valor inicial → alvo", f"{m.get('valor_inicial','—')} → {m.get('valor_alvo','—')}"),
                ("Progresso",            f"{m.get('progresso_percentual', 0):.0f}%"),
                ("Prazo",                data_lim_txt),
            ]))
            story.append(Spacer(1, 6))

    # ── Evoluções ───────────────────────────────────────────
    story.append(Paragraph(f"Evoluções Clínicas ({len(evolucoes)})", styles["secao"]))
    if not evolucoes:
        story.append(Paragraph("Nenhuma evolução registrada.", styles["valor"]))
    else:
        for i, ev in enumerate(reversed(evolucoes), 1):
            data = ev.get("criado_em")
            if isinstance(data, datetime):
                data_txt = data.strftime("%d/%m/%Y · %H:%M")
            else:
                data_txt = str(data)[:16] if data else "—"
            medicoes = ev.get("medicoes") or []
            med_txt  = " · ".join(
                f"{m.get('nome_indicador','?')}: {m.get('valor_registrado','?')} {m.get('unidade','')}"
                for m in medicoes
            ) or "Sem medições"
            story.append(_kv_table([
                (f"Sessão #{i}",  data_txt),
                ("Status",        ev.get("status", "—")),
                ("Medições",       med_txt),
                ("Feedback docente", ev.get("feedback_docente") or "—"),
            ]))
            story.append(Spacer(1, 6))

    # ── Equipe Supervisora (docentes que revisaram evoluções) ─
    story.append(Paragraph("Equipe Supervisora", styles["secao"]))
    if not docentes_revisores:
        story.append(Paragraph(
            "Nenhuma evolução deste prontuário foi revisada por docente até o momento.",
            styles["valor"]
        ))
    else:
        linhas_doc = []
        for d in docentes_revisores:
            linhas_doc.append((
                d.get("nome_completo", "—"),
                f"Mat. {d.get('matricula','—')} · {d.get('email','—')} · "
                f"<b>{d.get('total_revisoes', 0)}</b> evolução(ões) revisada(s)"
            ))
        story.append(_kv_table(linhas_doc, col_label_width=6 * cm))

    # ── Assinaturas ─────────────────────────────────────────
    story.append(Paragraph("Assinaturas Digitais", styles["secao"]))
    story += _bloco_assinaturas(relatorio, styles)

    doc.build(story)
    buffer.seek(0)
    # Relatório completo NÃO leva marca d'água (é técnico/interno)
    return buffer.getvalue()
