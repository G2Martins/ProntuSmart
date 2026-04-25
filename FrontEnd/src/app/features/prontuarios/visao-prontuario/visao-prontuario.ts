import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { PacienteService } from '../../../core/services/paciente.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';
import { MetaSmartService } from '../../../core/services/meta-smart.service';
import { AuthService } from '../../../core/services/auth.service';
import { IndicadorService } from '../../../core/services/indicador.service';
import { TesteService, Teste, TipoTeste } from '../../../core/services/teste.service';
import { Indicador } from '../../../shared/models/indicador.model';
import { descreverLimitesIndicador, valorForaDoLimite } from '../../../shared/utils/indicador-limites';

@Component({
  selector: 'app-visao-prontuario',
  standalone: true,
  imports: [CommonModule, FormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './visao-prontuario.html',
  styleUrl: './visao-prontuario.scss',
})
export class VisaoProntuario implements OnInit {
  private route             = inject(ActivatedRoute);
  protected router          = inject(Router);
  private prontuarioService = inject(ProntuarioService);
  private pacienteService   = inject(PacienteService);
  private evolucaoService   = inject(EvolucaoService);
  private metaService       = inject(MetaSmartService);
  private authService       = inject(AuthService);
  private cdr               = inject(ChangeDetectorRef);
  private indicadorService  = inject(IndicadorService);
  private testeService      = inject(TesteService);

  prontuario: any   = null;
  paciente: any     = null;
  evolucoes: any[]  = [];
  metas: any[]      = [];
  indicadores: Indicador[] = [];
  testes: Teste[]   = [];

  isLoadingProntuario  = true;
  isLoadingEvolucoes   = true;
  isLoadingMetas       = true;
  isLoadingIndicadores = false;
  isLoadingTestes      = true;

  perfil: string | null = '';
  abaAtiva: 'evolucoes' | 'metas' | 'graficos' | 'testes' | 'detalhado' = 'evolucoes';

  // Modal Novo Teste
  modalNovoTesteAberto = false;
  testeExpandidoId: string | null = null;
  coordenacaoItens = [
    { ctrl: 'coordenacao_decomposicao_movimentos', label: 'Decomposição de Movimentos' },
    { ctrl: 'coordenacao_ataxia_cerebelar', label: 'Ataxia Cerebelar' },
    { ctrl: 'coordenacao_dismetria', label: 'Dismetria' },
    { ctrl: 'coordenacao_nistagmo', label: 'Nistagmo' },
    { ctrl: 'coordenacao_rechaco_stewart_holmes', label: 'Rechaço de Stewart-Holmes' },
  ];

  // ── SVG Chart constants ────────────────────────────────────
  readonly svgW   = 560;
  readonly svgH   = 200;
  readonly svgPad = { top: 16, right: 28, bottom: 44, left: 52 };

  // ── Modal de Edição de Meta ──────────────────────────────
  modalEditarAberto    = false;
  metaEmEdicao: any    = null;
  editEspecifico       = '';
  editCriterio         = '';
  editCondicao         = '';
  editAtingivelResposta = 'sim';
  editAlcancavel       = '';
  editRelevante        = '';
  editValorAlvo        = 0;
  editDataLimite       = '';
  editDataReavaliacao  = '';
  isSalvandoEdicao     = false;

  // ── Modal de Cancelamento de Meta ───────────────────────
  modalCancelarAberto  = false;
  metaParaCancelar: any = null;
  motivoCancelamento   = '';
  isCancelando         = false;

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    const id    = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarProntuario(id);
      this.carregarEvolucoes(id);
      this.carregarMetas(id);
      this.carregarIndicadores();
      this.carregarTestes(id);
    }
  }

  carregarTestes(prontuarioId: string) {
    this.isLoadingTestes = true;
    this.testeService.listarPorProntuario(prontuarioId).subscribe({
      next: (lista) => {
        this.testes = lista;
        this.isLoadingTestes = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoadingTestes = false; this.cdr.detectChanges(); }
    });
  }

  abrirNovoTeste() {
    this.modalNovoTesteAberto = true;
    this.cdr.detectChanges();
  }

  fecharNovoTeste() {
    this.modalNovoTesteAberto = false;
    this.cdr.detectChanges();
  }

  iniciarTeste(tipo: TipoTeste) {
    this.modalNovoTesteAberto = false;
    if (tipo === 'AvaliacaoFuncional') {
      this.router.navigate(['/prontuarios/avaliacao', this.prontuario._id]);
    } else if (tipo === 'Sunny') {
      this.router.navigate(['/prontuarios/teste-sunny', this.prontuario._id]);
    } else if (tipo === 'MiniBest') {
      this.router.navigate(['/prontuarios/teste-mini-best', this.prontuario._id]);
    }
  }

  abrirTeste(t: Teste) {
    if (!t._id) return;
    if (t.tipo === 'Sunny') {
      this.router.navigate(['/prontuarios/teste-sunny/visualizar', t._id]);
    } else if (t.tipo === 'MiniBest') {
      this.router.navigate(['/prontuarios/teste-mini-best/visualizar', t._id]);
    }
  }

  excluirTeste(t: Teste, ev: Event) {
    ev.stopPropagation();
    if (!t._id) return;
    if (!confirm(`Excluir o teste ${this.tipoTesteLabel(t.tipo)}?`)) return;
    this.testeService.excluir(t._id).subscribe({
      next: () => this.carregarTestes(this.prontuario._id),
      error: () => alert('Erro ao excluir teste.')
    });
  }

  tipoTesteLabel(tipo: TipoTeste): string {
    const map: Record<TipoTeste, string> = {
      AvaliacaoFuncional: 'Avaliação Funcional',
      Sunny:              'Escala de Sunny',
      MiniBest:           'Mini-BESTest',
    };
    return map[tipo] || tipo;
  }

  tipoTesteIcone(tipo: TipoTeste): string {
    const map: Record<TipoTeste, string> = {
      AvaliacaoFuncional: 'ph:clipboard-text-bold',
      Sunny:              'ph:sun-bold',
      MiniBest:           'ph:scales-bold',
    };
    return map[tipo] || 'ph:test-tube-bold';
  }

  tipoTesteCor(tipo: TipoTeste): string {
    const map: Record<TipoTeste, string> = {
      AvaliacaoFuncional: 'bg-blue-100 text-blue-600',
      Sunny:              'bg-amber-100 text-amber-600',
      MiniBest:           'bg-purple-100 text-purple-600',
    };
    return map[tipo] || 'bg-gray-100 text-gray-600';
  }

  // "Avaliação Funcional" virtual — derivada do prontuário para listar como teste
  get testesComAvalFuncional(): any[] {
    const lista: any[] = [...this.testes];
    if (this.secaoAvaliacaoPreenchida()) {
      lista.unshift({
        _id: 'avaliacao-funcional-virtual',
        tipo: 'AvaliacaoFuncional' as TipoTeste,
        data_aplicacao: this.prontuario?.atualizado_em || this.prontuario?.criado_em,
        criado_em: this.prontuario?.atualizado_em || this.prontuario?.criado_em,
        nome_aplicador: this.prontuario?.nome_estagiario,
        interpretacao: this.prontuario?.problema_funcional_prioritario || null,
        _virtual: true,
      });
    }
    return lista;
  }

  abrirAvalFuncional() {
    if (this.prontuario?._id) {
      this.router.navigate(['/prontuarios/avaliacao', this.prontuario._id]);
    }
  }

  carregarProntuario(id: string) {
    this.isLoadingProntuario = true;
    this.prontuarioService.buscarPorId(id).subscribe({
      next: (pront) => {
        this.prontuario          = pront;
        this.isLoadingProntuario = false;
        this.cdr.detectChanges();
        if (pront.paciente_id) {
          this.pacienteService.buscarPorId(pront.paciente_id).subscribe({
            next: (pac) => { this.paciente = pac; this.cdr.detectChanges(); }
          });
        }
      },
      error: () => { this.isLoadingProntuario = false; this.cdr.detectChanges(); }
    });
  }

  carregarEvolucoes(prontuarioId: string) {
    this.isLoadingEvolucoes = true;
    this.evolucaoService.listarPorProntuario(prontuarioId).subscribe({
      next: (evs) => { this.evolucoes = evs; this.isLoadingEvolucoes = false; this.cdr.detectChanges(); },
      error: () => { this.isLoadingEvolucoes = false; this.cdr.detectChanges(); }
    });
  }

  carregarMetas(prontuarioId: string) {
    this.isLoadingMetas = true;
    this.metaService.listarPorProntuario(prontuarioId).subscribe({
      next: (metas) => { this.metas = metas; this.isLoadingMetas = false; this.cdr.detectChanges(); },
      error: () => { this.isLoadingMetas = false; this.cdr.detectChanges(); }
    });
  }

  // ── Edição de Meta ────────────────────────────────────────
  abrirModalEditar(meta: any) {
    this.metaEmEdicao       = meta;
    this.editEspecifico     = meta.especifico     || '';
    this.editCriterio       = meta.criterio_mensuravel || '';
    this.editCondicao       = meta.condicao_execucao   || '';
    this.editAtingivelResposta = this.inferirAtingivel(meta.alcancavel);
    this.editAlcancavel     = this.editAtingivelResposta === 'sim' ? (meta.alcancavel || '') : '';
    this.editRelevante      = meta.relevante      || '';
    this.editValorAlvo      = meta.valor_alvo     || 0;
    this.editDataLimite     = meta.data_limite
      ? new Date(meta.data_limite).toISOString().split('T')[0] : '';
    this.editDataReavaliacao = meta.data_reavaliacao
      ? new Date(meta.data_reavaliacao).toISOString().split('T')[0] : '';
    this.modalEditarAberto  = true;
    this.cdr.detectChanges();
  }

  fecharModalEditar() {
    this.modalEditarAberto = false;
    this.metaEmEdicao      = null;
    this.cdr.detectChanges();
  }

  onEditAtingivelChange() {
    if (this.editAtingivelResposta === 'nao') {
      this.editAlcancavel = '';
    }
  }

  get indicadorMetaEmEdicao(): Indicador | null {
    if (!this.metaEmEdicao?.indicador_id) return null;
    return this.indicadores.find(ind => ind._id === this.metaEmEdicao.indicador_id) || null;
  }

  get descricaoLimitesMetaEmEdicao(): string {
    return descreverLimitesIndicador(this.indicadorMetaEmEdicao);
  }

  get editValorAlvoForaDoLimite(): boolean {
    return valorForaDoLimite(this.indicadorMetaEmEdicao, this.editValorAlvo);
  }

  salvarEdicao() {
    if (!this.metaEmEdicao) return;
    if (this.editAtingivelResposta === 'sim' && !this.editAlcancavel.trim()) return;
    if (this.editValorAlvoForaDoLimite) return;
    this.isSalvandoEdicao = true;

    const payload = {
      especifico:          this.editEspecifico,
      criterio_mensuravel: this.editCriterio,
      condicao_execucao:   this.editCondicao,
      alcancavel:          this.editAtingivelResposta === 'sim' ? this.editAlcancavel : 'N\u00E3o',
      relevante:           this.editRelevante,
      valor_alvo:          this.editValorAlvo,
      data_limite:         this.editDataLimite    ? new Date(this.editDataLimite).toISOString()    : undefined,
      data_reavaliacao:    this.editDataReavaliacao ? new Date(this.editDataReavaliacao).toISOString() : undefined,
    };

    this.metaService.editar(this.metaEmEdicao._id, payload).subscribe({
      next: () => {
        this.isSalvandoEdicao = false;
        this.fecharModalEditar();
        this.carregarMetas(this.prontuario._id);
      },
      error: () => { this.isSalvandoEdicao = false; this.cdr.detectChanges(); }
    });
  }

  // ── Cancelamento de Meta ─────────────────────────────────
  abrirModalCancelar(meta: any) {
    this.metaParaCancelar  = meta;
    this.motivoCancelamento = '';
    this.modalCancelarAberto = true;
    this.cdr.detectChanges();
  }

  fecharModalCancelar() {
    this.modalCancelarAberto = false;
    this.metaParaCancelar   = null;
    this.motivoCancelamento  = '';
    this.cdr.detectChanges();
  }

  confirmarCancelamento() {
    if (!this.metaParaCancelar || !this.motivoCancelamento.trim()) return;
    this.isCancelando = true;

    this.metaService.cancelar(this.metaParaCancelar._id, 'Cancelada', this.motivoCancelamento).subscribe({
      next: () => {
        this.isCancelando = false;
        this.fecharModalCancelar();
        this.carregarMetas(this.prontuario._id);
      },
      error: () => { this.isCancelando = false; this.cdr.detectChanges(); }
    });
  }

  metaPodeSerEditada(meta: any): boolean {
    return !['Cancelada', 'Concluída', 'Substituída'].includes(meta.status);
  }

  // ── Helpers de UI ─────────────────────────────────────────
  irParaNovaEvolucao()  { this.router.navigate(['/prontuarios/evoluir', this.prontuario._id]); }
  voltar()              { this.router.navigate(['/pacientes']); }

  // ── Helpers para a aba "Ficha Detalhada" ─────────────────
  fmt(val: any): string {
    if (val === null || val === undefined || val === '') return '—';
    return String(val);
  }

  fmtBool(val: boolean | null | undefined): string {
    if (val === true)  return 'Sim';
    if (val === false) return 'Não';
    return '—';
  }

  fmtMarcacao(val: boolean | null | undefined): string {
    return val === true ? 'Marcado' : '—';
  }

  fmtDeambulacao(val: string | boolean | null | undefined): string {
    if (typeof val === 'string') return this.fmt(val);
    return this.fmtBool(val);
  }

  getBoolClass(val: boolean | null | undefined): string {
    if (val === true)  return 'bg-green-50 text-green-700 border-green-200';
    if (val === false) return 'bg-red-50 text-red-700 border-red-200';
    return 'bg-gray-50 text-gray-500 border-gray-200';
  }

  getMarcacaoClass(val: boolean | null | undefined): string {
    if (val === true) return 'bg-green-50 text-green-700 border-green-200';
    return 'bg-gray-50 text-gray-500 border-gray-200';
  }

  getDeambulacaoClass(val: string | boolean | null | undefined): string {
    if (typeof val === 'string') return this.getNivelClass(val);
    return this.getBoolClass(val);
  }

  getAvdLabel(val: string | null | undefined): string {
    const map: any = {
      'I':  'Independente',
      'S':  'Supervisão',
      'AP': 'Ajuda parcial',
      'D':  'Dependente'
    };
    return val ? (map[val] || val) : '—';
  }

  getAvdClass(val: string | null | undefined): string {
    switch (val) {
      case 'I':  return 'bg-green-50 text-green-700 border-green-200';
      case 'S':  return 'bg-blue-50  text-blue-700  border-blue-200';
      case 'AP': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'D':  return 'bg-red-50   text-red-700   border-red-200';
      default:   return 'bg-gray-50  text-gray-400  border-gray-200';
    }
  }

  getNivelClass(val: string | null | undefined): string {
    if (!val) return 'bg-gray-50 text-gray-400 border-gray-200';
    const v = val.toLowerCase();
    if (v.includes('independente') || v.includes('preservad') || v.includes('baixo')) return 'bg-green-50 text-green-700 border-green-200';
    if (v.includes('supervis')     || v.includes('alterad')   || v.includes('moder')) return 'bg-blue-50  text-blue-700  border-blue-200';
    if (v.includes('parcial')      || v.includes('apoio'))                            return 'bg-amber-50 text-amber-700 border-amber-200';
    if (v.includes('dependente')   || v.includes('comprometid') || v.includes('alto') || v.includes('não')) return 'bg-red-50 text-red-700 border-red-200';
    return 'bg-gray-50 text-gray-600 border-gray-200';
  }

  // ── Completude da ficha clínica ──────────────────────────
  secaoTriagemPreenchida(): boolean {
    if (!this.prontuario) return false;
    return !!(this.prontuario.diagnostico_medico || this.prontuario.diagnostico_fisioterapeutico ||
              this.prontuario.queixa_principal   || this.prontuario.objetivo_paciente);
  }

  secaoAvaliacaoPreenchida(): boolean {
    if (!this.prontuario) return false;
    return !!(this.prontuario.sedestacao || this.prontuario.ortostatismo || this.prontuario.transferencias ||
              this.prontuario.realiza_marcha || this.prontuario.marcha_dispositivo || this.prontuario.marcha_dispositivo_descricao ||
              this.prontuario.funcao_mmss || this.prontuario.funcao_mmii || this.prontuario.equilibrio ||
              this.prontuario.coordenacao_decomposicao_movimentos || this.prontuario.coordenacao_ataxia_cerebelar ||
              this.prontuario.coordenacao_dismetria || this.prontuario.coordenacao_nistagmo ||
              this.prontuario.coordenacao_rechaco_stewart_holmes ||
              this.prontuario.avd_banho   || this.prontuario.avd_vestir);
  }

  secaoSintesePreenchida(): boolean {
    if (!this.prontuario) return false;
    return !!(this.prontuario.problema_funcional_prioritario || this.prontuario.atividade_comprometida ||
              this.prontuario.impacto_independencia          || this.prontuario.prioridade_terapeutica);
  }

  percentualPreenchimento(): number {
    if (!this.prontuario) return 0;
    const campos = [
      'diagnostico_medico','diagnostico_fisioterapeutico','queixa_principal','objetivo_paciente',
      'comorbidades','medicamentos','barreiras_ambientais',
      'sedestacao','ortostatismo','transferencias','realiza_marcha','marcha_dispositivo','marcha_dispositivo_descricao',
      'funcao_mmss','funcao_mmii','equilibrio','risco_queda','dor','fadiga_funcional',
      'compreende_comandos','comunicacao_preservada',
      'coordenacao_decomposicao_movimentos','coordenacao_ataxia_cerebelar','coordenacao_dismetria',
      'coordenacao_nistagmo','coordenacao_rechaco_stewart_holmes',
      'avd_banho','avd_vestir','avd_higiene','avd_locomocao','avd_alimentacao','avd_banheiro',
      'atividade_mais_impactada','principal_limitacao','teste_escala_principal','valor_teste_inicial',
      'problema_funcional_prioritario','atividade_comprometida','impacto_independencia','prioridade_terapeutica'
    ];
    const preenchidos = campos.filter(c => {
      const v = this.prontuario[c];
      return v !== null && v !== undefined && v !== '';
    }).length;
    return Math.round((preenchidos / campos.length) * 100);
  }

  calcularIdade(dataNascimento: string): number {
    if (!dataNascimento) return 0;
    const hoje = new Date(); const nasc = new Date(dataNascimento);
    let idade = hoje.getFullYear() - nasc.getFullYear();
    const m = hoje.getMonth() - nasc.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
    return idade;
  }

  getStatusProntuarioClass(s: string) {
    return ({ Ativo: 'bg-green-100 text-green-700 border-green-200', Alta: 'bg-blue-100 text-blue-700 border-blue-200', Encaminhado: 'bg-orange-100 text-orange-700 border-orange-200' } as any)[s] || 'bg-gray-100 text-gray-700';
  }
  getEvolucaoStatusClass(s: string) {
    return ({ 'Pendente de Revisão': 'bg-orange-100 text-orange-700', 'Aprovado e Assinado': 'bg-green-100 text-green-700', 'Ajustes Solicitados': 'bg-red-100 text-red-700' } as any)[s] || 'bg-gray-100 text-gray-600';
  }
  getEvolucaoStatusIcon(s: string) {
    return ({ 'Pendente de Revisão': 'ph:clock-countdown-bold', 'Aprovado e Assinado': 'ph:seal-check-bold', 'Ajustes Solicitados': 'ph:warning-circle-bold' } as any)[s] || 'ph:clock-bold';
  }
  getEvolucaoIconColor(s: string) {
    return ({ 'Pendente de Revisão': 'bg-orange-100 text-orange-600', 'Aprovado e Assinado': 'bg-green-100 text-green-600', 'Ajustes Solicitados': 'bg-red-100 text-red-600' } as any)[s] || 'bg-gray-100 text-gray-500';
  }
  getMetaStatusClass(s: string) {
    return ({ 'Não iniciada': 'bg-gray-100 text-gray-600 border-gray-200', 'Em andamento': 'bg-blue-100 text-blue-700 border-blue-200', 'Parcialmente atingida': 'bg-yellow-100 text-yellow-700 border-yellow-200', 'Concluída': 'bg-green-100 text-green-700 border-green-200', 'Não atingida': 'bg-red-100 text-red-700 border-red-200', 'Substituída': 'bg-purple-100 text-purple-700 border-purple-200', 'Cancelada': 'bg-gray-200 text-gray-500 border-gray-300' } as any)[s] || 'bg-gray-100 text-gray-600 border-gray-200';
  }
  inferirAtingivel(valor: string | null | undefined): 'sim' | 'nao' {
    const normalizado = String(valor || '').trim().toLowerCase();
    return normalizado === 'n\u00E3o' || normalizado === 'nao' ? 'nao' : 'sim';
  }

  getRespostaAtingivel(valor: string | null | undefined): string {
    return this.inferirAtingivel(valor) === 'sim' ? 'Sim' : 'N\u00E3o';
  }

  temJustificativaAtingivel(valor: string | null | undefined): boolean {
    return this.inferirAtingivel(valor) === 'sim';
  }

  getProgressoColor(pct: number) {
    if (pct >= 100) return 'bg-green-500';
    if (pct >= 60)  return 'bg-blue-500';
    if (pct >= 30)  return 'bg-yellow-500';
    return 'bg-orange-400';
  }

  // ── Indicadores / Gráficos ───────────────────────────────
  carregarIndicadores() {
    this.isLoadingIndicadores = true;
    this.indicadorService.listar(false).subscribe({
      next: (inds) => {
        this.indicadores = inds;
        this.isLoadingIndicadores = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoadingIndicadores = false; this.cdr.detectChanges(); }
    });
  }

  get isLoadingGraficos(): boolean {
    return this.isLoadingEvolucoes || this.isLoadingMetas || this.isLoadingIndicadores;
  }

  get dadosGraficos(): any[] {
    const series = new Map<string, any>();

    // 1. Seed from metas: valor_inicial como ponto de partida
    for (const meta of this.metas) {
      if (!meta.indicador_id) continue;
      const indId  = String(meta.indicador_id);
      const ind    = this.indicadores.find(i => i._id === indId);

      if (!series.has(indId)) {
        const pontoInicial: any[] = (meta.valor_inicial != null && meta.criado_em)
          ? [{ data: new Date(meta.criado_em), valor: Number(meta.valor_inicial), label: 'Inicial' }]
          : [];
        series.set(indId, {
          indicador_id:    indId,
          nome:            ind?.nome            || 'Indicador',
          unidade:         ind?.unidade_medida  || '',
          direcao_melhora: ind?.direcao_melhora || 'maior_melhor',
          valor_alvo:      meta.valor_alvo ?? null,
          pontos:          pontoInicial,
        });
      } else {
        // Se existir meta posterior, atualizar o alvo
        const s = series.get(indId)!;
        if (meta.valor_alvo != null) s.valor_alvo = meta.valor_alvo;
      }
    }

    // 2. Adicionar medições das evoluções (ordem cronológica)
    const evs = [...this.evolucoes].sort(
      (a, b) => new Date(a.criado_em).getTime() - new Date(b.criado_em).getTime()
    );
    for (const ev of evs) {
      for (const med of (ev.medicoes || [])) {
        if (!med.indicador_id) continue;
        const indId = String(med.indicador_id);
        const valor = parseFloat(String(med.valor_registrado));
        if (isNaN(valor)) continue;

        if (!series.has(indId)) {
          const ind = this.indicadores.find(i => i._id === indId);
          series.set(indId, {
            indicador_id:    indId,
            nome:            med.nome_indicador || ind?.nome            || 'Indicador',
            unidade:         med.unidade        || ind?.unidade_medida  || '',
            direcao_melhora: ind?.direcao_melhora || 'maior_melhor',
            valor_alvo:      null,
            pontos:          [],
          });
        }

        const s = series.get(indId)!;
        if (!s.nome || s.nome === 'Indicador') s.nome = med.nome_indicador || s.nome;
        if (!s.unidade) s.unidade = med.unidade || '';
        s.pontos.push({ data: new Date(ev.criado_em), valor });
      }
    }

    return Array.from(series.values()).filter(s => s.pontos.length >= 1);
  }

  // ── SVG helpers (chart internals) ────────────────────────
  private get plotW(): number { return this.svgW - this.svgPad.left - this.svgPad.right; }
  private get plotH(): number { return this.svgH - this.svgPad.top  - this.svgPad.bottom; }

  private yBounds(pontos: { valor: number }[], valorAlvo: number | null) {
    const vals   = pontos.map(p => p.valor);
    if (valorAlvo != null) vals.push(valorAlvo);
    const rawMin = Math.min(...vals);
    const rawMax = Math.max(...vals);
    const range  = rawMax - rawMin;
    const pad    = range * 0.15 || Math.abs(rawMin) * 0.1 || 5;
    return { min: rawMin - pad, max: rawMax + pad };
  }

  calcularSvgPts(pontos: { valor: number }[], valorAlvo: number | null): string {
    if (!pontos.length) return '';
    const { min, max } = this.yBounds(pontos, valorAlvo);
    const r = max - min || 1;
    return pontos.map((p, i) => {
      const x = this.svgPad.left + (pontos.length > 1 ? (i / (pontos.length - 1)) * this.plotW : this.plotW / 2);
      const y = this.svgPad.top  + this.plotH - ((p.valor - min) / r) * this.plotH;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
  }

  calcularAreaPath(pontos: { valor: number }[], valorAlvo: number | null): string {
    if (pontos.length < 2) return '';
    const { min, max } = this.yBounds(pontos, valorAlvo);
    const r        = max - min || 1;
    const baseline = this.svgH - this.svgPad.bottom;
    const pts      = pontos.map((p, i) => ({
      x: this.svgPad.left + (i / (pontos.length - 1)) * this.plotW,
      y: this.svgPad.top  + this.plotH - ((p.valor - min) / r) * this.plotH,
    }));
    const line = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
    return `${line} L${pts[pts.length - 1].x.toFixed(1)},${baseline} L${pts[0].x.toFixed(1)},${baseline} Z`;
  }

  getXCoord(i: number, n: number): number {
    return this.svgPad.left + (n > 1 ? (i / (n - 1)) * this.plotW : this.plotW / 2);
  }

  getYCoord(valor: number, pontos: { valor: number }[], valorAlvo: number | null): number {
    const { min, max } = this.yBounds(pontos, valorAlvo);
    const r = max - min || 1;
    return this.svgPad.top + this.plotH - ((valor - min) / r) * this.plotH;
  }

  getYTicks(pontos: { valor: number }[], valorAlvo: number | null): { y: number; label: string }[] {
    const { min, max } = this.yBounds(pontos, valorAlvo);
    const r = max - min || 1;
    return [0, 0.25, 0.5, 0.75, 1].map(t => {
      const val = min + r * t;
      const y   = this.svgPad.top + this.plotH * (1 - t);
      return { y: parseFloat(y.toFixed(1)), label: val % 1 === 0 ? val.toFixed(0) : val.toFixed(1) };
    });
  }

  formatDataCurta(d: Date | string): string {
    const dt = d instanceof Date ? d : new Date(d);
    return `${dt.getDate().toString().padStart(2, '0')}/${(dt.getMonth() + 1).toString().padStart(2, '0')}`;
  }

  getCorLinha(serie: { pontos: { valor: number }[]; direcao_melhora: string }): string {
    if (serie.pontos.length < 2) return '#3b82f6';
    const prev = serie.pontos[0].valor;
    const curr = serie.pontos[serie.pontos.length - 1].valor;
    if (prev === curr) return '#6b7280';
    const melhora = serie.direcao_melhora === 'maior_melhor' ? curr > prev : curr < prev;
    return melhora ? '#16a34a' : '#dc2626';
  }

  getCorLinhaClass(serie: { pontos: { valor: number }[]; direcao_melhora: string }): string {
    if (serie.pontos.length < 2) return 'text-blue-600';
    const prev = serie.pontos[0].valor;
    const curr = serie.pontos[serie.pontos.length - 1].valor;
    if (prev === curr) return 'text-gray-600';
    const melhora = serie.direcao_melhora === 'maior_melhor' ? curr > prev : curr < prev;
    return melhora ? 'text-green-600' : 'text-red-600';
  }

  getTendenciaBadge(serie: { pontos: { valor: number }[]; direcao_melhora: string; unidade: string }): { texto: string; cor: string } {
    if (serie.pontos.length < 2) return { texto: '1 registro', cor: 'text-gray-400' };
    const prev = serie.pontos[0].valor;
    const curr = serie.pontos[serie.pontos.length - 1].valor;
    const diff = curr - prev;
    if (diff === 0) return { texto: 'Sem variação', cor: 'text-gray-500' };
    const pct      = Math.abs(diff / (prev || 1)) * 100;
    const melhora  = serie.direcao_melhora === 'maior_melhor' ? diff > 0 : diff < 0;
    const sinal    = diff > 0 ? '▲' : '▼';
    const absDiff  = Math.abs(diff);
    const diffStr  = absDiff % 1 === 0 ? absDiff.toFixed(0) : absDiff.toFixed(1);
    return {
      texto: `${sinal} ${diffStr} ${serie.unidade} (${pct.toFixed(0)}%)`,
      cor:   melhora ? 'text-green-600' : 'text-red-600',
    };
  }
}
