import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { DashboardService } from '../../../core/services/dashboard.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-inteligencia-epidemiologica',
  standalone: true,
  imports: [CommonModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './inteligencia-epidemiologica.html',
})
export class InteligenciaEpidemiologicaComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  protected router         = inject(Router);
  private cdr              = inject(ChangeDetectorRef);

  isLoading = true;
  erro      = '';

  // Dados de epidemiologia
  epidemiologia: any = null;
  // Dados de produtividade
  produtividade: any = null;
  // Dados de riscos
  riscos: any = null;

  ngOnInit() {
    this.carregarDados();
  }

  carregarDados() {
    this.isLoading = true;
    this.erro      = '';

    forkJoin({
      epi:  this.dashboardService.getEpidemiologia(),
      prod: this.dashboardService.getProdutividade(),
      risk: this.dashboardService.getRiscos(),
    }).subscribe({
      next: ({ epi, prod, risk }) => {
        this.epidemiologia = epi;
        this.produtividade = prod;
        this.riscos        = risk;
        this.isLoading     = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.erro      = 'Erro ao carregar dados do dashboard. Verifique a conexão com o servidor.';
        this.isLoading = false;
        this.cdr.detectChanges();
      },
    });
  }

  // Calcula largura da barra proporcional ao item de maior valor
  barWidth(value: number, list: any[], key: string): string {
    const max = Math.max(...list.map(i => i[key] || 0), 1);
    return `${Math.round((value / max) * 100)}%`;
  }

  // Retorna cor para barra conforme índice
  barColor(index: number): string {
    const colors = [
      'bg-blue-500', 'bg-purple-500', 'bg-emerald-500',
      'bg-orange-400', 'bg-pink-500', 'bg-teal-500',
      'bg-indigo-500', 'bg-yellow-500',
    ];
    return colors[index % colors.length];
  }

  // Cor do badge de prioridade de risco
  prioridadeClass(prioridade: string): string {
    return prioridade === 'alta'
      ? 'bg-red-100 text-red-700 border-red-200'
      : 'bg-yellow-100 text-yellow-700 border-yellow-200';
  }

  // Cor do ícone de risco
  tipoRiscoIcon(tipo: string): string {
    return tipo === 'meta_estagnada' ? 'ph:target-bold' : 'ph:activity-bold';
  }

  tipoRiscoColor(tipo: string): string {
    return tipo === 'meta_estagnada'
      ? 'bg-red-100 text-red-600'
      : 'bg-yellow-100 text-yellow-600';
  }

  get totalEvolucoes(): number {
    return this.produtividade?.totais_evolucoes?.total ?? 0;
  }

  get pctAprovadas(): number {
    const total = this.totalEvolucoes;
    if (!total) return 0;
    return Math.round((this.produtividade.totais_evolucoes.aprovadas / total) * 100);
  }

  get pctPendentes(): number {
    const total = this.totalEvolucoes;
    if (!total) return 0;
    return Math.round((this.produtividade.totais_evolucoes.pendentes / total) * 100);
  }
}
