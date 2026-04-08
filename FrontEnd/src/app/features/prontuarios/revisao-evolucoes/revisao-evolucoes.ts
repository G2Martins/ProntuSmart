import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { EvolucaoService } from '../../../core/services/evolucao.service';

@Component({
  selector: 'app-revisao-evolucoes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './revisao-evolucoes.html'
})
export class RevisaoEvolucoesComponent implements OnInit {
  private evolucaoService = inject(EvolucaoService);
  protected router        = inject(Router);
  private cdr             = inject(ChangeDetectorRef);

  evolucoes: any[]  = [];
  isLoading         = true;
  erro              = '';

  // Estado do modal de feedback
  modalAberto       = false;
  evolucaoSelecionada: any = null;
  feedbackTexto     = '';
  acaoAtual: 'aprovar' | 'devolver' | null = null;
  isProcessando     = false;

  ngOnInit() {
    this.carregarPendentes();
  }

  carregarPendentes() {
    this.isLoading = true;
    this.evolucaoService.listarPendentes().subscribe({
      next: (evs) => {
        this.evolucoes = evs;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.erro      = 'Erro ao carregar evoluções pendentes.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  abrirModal(evolucao: any, acao: 'aprovar' | 'devolver') {
    this.evolucaoSelecionada = evolucao;
    this.acaoAtual           = acao;
    this.feedbackTexto       = '';
    this.modalAberto         = true;
    this.cdr.detectChanges();
  }

  fecharModal() {
    this.modalAberto         = false;
    this.evolucaoSelecionada = null;
    this.acaoAtual           = null;
    this.feedbackTexto       = '';
    this.cdr.detectChanges();
  }

  confirmarRevisao() {
    if (!this.evolucaoSelecionada || !this.acaoAtual) return;
    if (this.acaoAtual === 'devolver' && !this.feedbackTexto.trim()) return;

    this.isProcessando = true;

    this.evolucaoService.revisar(
      this.evolucaoSelecionada._id,
      this.acaoAtual,
      this.feedbackTexto || undefined
    ).subscribe({
      next: () => {
        this.isProcessando = false;
        this.fecharModal();
        this.carregarPendentes(); // Recarrega a lista
      },
      error: () => {
        this.isProcessando = false;
        this.erro = 'Erro ao processar revisão.';
        this.cdr.detectChanges();
      }
    });
  }

  getStatusClass(status: string): string {
    const map: any = {
      'Pendente de Revisão': 'bg-orange-100 text-orange-700',
      'Aprovado e Assinado': 'bg-green-100 text-green-700',
      'Ajustes Solicitados': 'bg-red-100 text-red-700',
    };
    return map[status] || 'bg-gray-100 text-gray-600';
  }
}