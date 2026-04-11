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
import { Indicador } from '../../../shared/models/indicador.model';

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

  prontuario: any   = null;
  paciente: any     = null;
  evolucoes: any[]  = [];
  metas: any[]      = [];
  indicadores: Indicador[] = [];

  isLoadingProntuario  = true;
  isLoadingEvolucoes   = true;
  isLoadingMetas       = true;
  isLoadingIndicadores = false;

  perfil: string | null = '';
  abaAtiva: 'evolucoes' | 'metas' | 'graficos' = 'evolucoes';

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
    this.editAlcancavel     = meta.alcancavel     || '';
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

  salvarEdicao() {
    if (!this.metaEmEdicao) return;
    this.isSalvandoEdicao = true;

    const payload = {
      especifico:          this.editEspecifico,
      criterio_mensuravel: this.editCriterio,
      condicao_execucao:   this.editCondicao,
      alcancavel:          this.editAlcancavel,
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