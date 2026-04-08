import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { PacienteService } from '../../../core/services/paciente.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';
import { MetaSmartService } from '../../../core/services/meta-smart.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-visao-prontuario',
  standalone: true,
  imports: [CommonModule],
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

  prontuario: any    = null;
  paciente: any      = null;
  evolucoes: any[]   = [];
  metas: any[]       = [];

  isLoadingProntuario = true;
  isLoadingEvolucoes  = true;
  isLoadingMetas      = true;

  perfil: string | null = '';
  abaAtiva: 'evolucoes' | 'metas' = 'evolucoes';

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    const id    = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarProntuario(id);
      this.carregarEvolucoes(id);
      this.carregarMetas(id);
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
      next: (evs) => {
        this.evolucoes          = evs;
        this.isLoadingEvolucoes = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoadingEvolucoes = false; this.cdr.detectChanges(); }
    });
  }

  carregarMetas(prontuarioId: string) {
    this.isLoadingMetas = true;
    this.metaService.listarPorProntuario(prontuarioId).subscribe({
      next: (metas) => {
        this.metas          = metas;
        this.isLoadingMetas = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoadingMetas = false; this.cdr.detectChanges(); }
    });
  }

  irParaNovaEvolucao() {
    this.router.navigate(['/prontuarios/evoluir', this.prontuario._id]);
  }

  voltar() { this.router.navigate(['/pacientes']); }

  calcularIdade(dataNascimento: string): number {
    if (!dataNascimento) return 0;
    const hoje = new Date();
    const nasc = new Date(dataNascimento);
    let idade   = hoje.getFullYear() - nasc.getFullYear();
    const m     = hoje.getMonth() - nasc.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
    return idade;
  }

  getStatusProntuarioClass(status: string): string {
    const map: any = {
      'Ativo':       'bg-green-100 text-green-700 border-green-200',
      'Alta':        'bg-blue-100 text-blue-700 border-blue-200',
      'Encaminhado': 'bg-orange-100 text-orange-700 border-orange-200',
    };
    return map[status] || 'bg-gray-100 text-gray-700 border-gray-200';
  }

  getEvolucaoStatusClass(status: string): string {
    const map: any = {
      'Pendente de Revisão': 'bg-orange-100 text-orange-700',
      'Aprovado e Assinado': 'bg-green-100 text-green-700',
      'Ajustes Solicitados': 'bg-red-100 text-red-700',
    };
    return map[status] || 'bg-gray-100 text-gray-600';
  }

  getEvolucaoStatusIcon(status: string): string {
    const map: any = {
      'Pendente de Revisão': 'ph:clock-countdown-bold',
      'Aprovado e Assinado': 'ph:seal-check-bold',
      'Ajustes Solicitados': 'ph:warning-circle-bold',
    };
    return map[status] || 'ph:clock-bold';
  }

  getEvolucaoIconColor(status: string): string {
    const map: any = {
      'Pendente de Revisão': 'bg-orange-100 text-orange-600',
      'Aprovado e Assinado': 'bg-green-100 text-green-600',
      'Ajustes Solicitados': 'bg-red-100 text-red-600',
    };
    return map[status] || 'bg-gray-100 text-gray-500';
  }

  getMetaStatusClass(status: string): string {
    const map: any = {
      'Não iniciada':        'bg-gray-100 text-gray-600 border-gray-200',
      'Em andamento':        'bg-blue-100 text-blue-700 border-blue-200',
      'Parcialmente atingida': 'bg-yellow-100 text-yellow-700 border-yellow-200',
      'Atingida':            'bg-green-100 text-green-700 border-green-200',
      'Não atingida':        'bg-red-100 text-red-700 border-red-200',
      'Substituída':         'bg-purple-100 text-purple-700 border-purple-200',
    };
    return map[status] || 'bg-gray-100 text-gray-600 border-gray-200';
  }

  getProgressoColor(pct: number): string {
    if (pct >= 100) return 'bg-green-500';
    if (pct >= 60)  return 'bg-blue-500';
    if (pct >= 30)  return 'bg-yellow-500';
    return 'bg-orange-400';
  }
}