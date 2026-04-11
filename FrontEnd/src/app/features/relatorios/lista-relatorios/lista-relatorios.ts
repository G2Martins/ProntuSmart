import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { RelatorioService } from '../../../core/services/relatorio.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { AuthService } from '../../../core/services/auth.service';

interface PacienteVinculado {
  prontuario_id: string;
  numero_prontuario: string;
  paciente_id: string;
  nome_paciente: string;
  area_atendimento: string;
  nome_estagiario?: string;
}

@Component({
  selector: 'app-lista-relatorios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './lista-relatorios.html'
})
export class ListaRelatoriosComponent implements OnInit {
  private relatorioService  = inject(RelatorioService);
  private prontuarioService = inject(ProntuarioService);
  private authService       = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  protected router = inject(Router);

  perfil = this.authService.getUserProfile();

  pacientes:  PacienteVinculado[] = [];
  relatorios: any[] = [];
  isLoadingPacientes  = true;
  isLoadingRelatorios = true;
  errorMessage = '';

  // Filtros
  filtroPaciente = '';
  filtroStatus   = '';
  filtroTipo     = '';

  abaAtiva: 'novo' | 'historico' = 'novo';

  ngOnInit() {
    this.carregarPacientes();
    this.carregarRelatorios();
  }

  carregarPacientes() {
    this.isLoadingPacientes = true;
    this.prontuarioService.listarMeusProntuarios().subscribe({
      next: (prontuarios) => {
        this.pacientes = prontuarios.map((p: any) => ({
          prontuario_id: p._id,
          numero_prontuario: p.numero_prontuario,
          paciente_id: p.paciente_id,
          nome_paciente: p.nome_paciente || '—',
          area_atendimento: p.area_atendimento,
          nome_estagiario: p.nome_estagiario,
        }));
        this.isLoadingPacientes = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Erro ao carregar pacientes vinculados.';
        this.isLoadingPacientes = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarRelatorios() {
    this.isLoadingRelatorios = true;
    this.relatorioService.listarMeus().subscribe({
      next: (rels) => {
        this.relatorios = rels;
        this.isLoadingRelatorios = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingRelatorios = false;
        this.cdr.detectChanges();
      }
    });
  }

  get pacientesFiltrados(): PacienteVinculado[] {
    if (!this.filtroPaciente.trim()) return this.pacientes;
    const t = this.filtroPaciente.toLowerCase();
    return this.pacientes.filter(p =>
      (p.nome_paciente || '').toLowerCase().includes(t) ||
      (p.numero_prontuario || '').toLowerCase().includes(t) ||
      (p.area_atendimento  || '').toLowerCase().includes(t)
    );
  }

  get relatoriosFiltrados(): any[] {
    return this.relatorios.filter(r => {
      if (this.filtroStatus && r.status !== this.filtroStatus) return false;
      if (this.filtroTipo   && r.tipo   !== this.filtroTipo)   return false;
      if (this.filtroPaciente.trim()) {
        const t = this.filtroPaciente.toLowerCase();
        const matches = (r.nome_paciente || '').toLowerCase().includes(t) ||
                        (r.numero_relatorio || '').toLowerCase().includes(t);
        if (!matches) return false;
      }
      return true;
    });
  }

  novoRelatorio(p: PacienteVinculado) {
    this.router.navigate(['/relatorios/novo', p.prontuario_id]);
  }

  abrirRelatorio(r: any) {
    this.router.navigate(['/relatorios/visualizar', r._id]);
  }

  baixarPdf(r: any, event: Event) {
    event.stopPropagation();
    this.relatorioService.baixarPdf(r._id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.target = '_blank';
        a.download = `${r.numero_relatorio}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: () => alert('Erro ao baixar o PDF do relatório.')
    });
  }

  cancelarRelatorio(r: any, event: Event) {
    event.stopPropagation();
    if (!confirm(`Excluir o rascunho ${r.numero_relatorio}?`)) return;
    this.relatorioService.cancelar(r._id).subscribe({
      next: () => this.carregarRelatorios(),
      error: () => alert('Erro ao excluir relatório.')
    });
  }

  getStatusClass(s: string): string {
    return ({
      'Rascunho':                          'bg-gray-100 text-gray-700 border-gray-200',
      'Aguardando Assinatura do Docente':  'bg-amber-100 text-amber-700 border-amber-200',
      'Finalizado':                        'bg-green-100 text-green-700 border-green-200',
      'Cancelado':                         'bg-red-100 text-red-700 border-red-200'
    } as any)[s] || 'bg-gray-100 text-gray-700';
  }

  getStatusIcon(s: string): string {
    return ({
      'Rascunho':                          'ph:pencil-bold',
      'Aguardando Assinatura do Docente':  'ph:clock-countdown-bold',
      'Finalizado':                        'ph:seal-check-bold',
      'Cancelado':                         'ph:x-circle-bold'
    } as any)[s] || 'ph:file-bold';
  }

  getTipoBadge(t: string): string {
    return t === 'Completo'
      ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
      : 'bg-blue-50 text-blue-700 border-blue-200';
  }

  // Estatísticas rápidas
  get statRascunhos(): number {
    return this.relatorios.filter(r => r.status === 'Rascunho').length;
  }
  get statAguardando(): number {
    return this.relatorios.filter(r => r.status === 'Aguardando Assinatura do Docente').length;
  }
  get statFinalizados(): number {
    return this.relatorios.filter(r => r.status === 'Finalizado').length;
  }
}
