import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { AuthService }       from '../../../core/services/auth.service';

interface AreaGrupo {
  nome:       string;
  prontuarios: any[];
  aberto:     boolean;
}

@Component({
  selector: 'app-busca-pacientes',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './busca-pacientes.html'
})
export class BuscaPacientesComponent implements OnInit {
  private prontuarioService = inject(ProntuarioService);
  private authService       = inject(AuthService);
  private cdr               = inject(ChangeDetectorRef);
  private router            = inject(Router);

  perfil       = this.authService.getUserProfile();
  isLoading    = true;
  errorMessage = '';
  termoBusca   = '';

  areasGrupos: AreaGrupo[] = [];

  ngOnInit() {
    this.carregarBase();
  }

  carregarBase() {
    this.isLoading = true;
    this.prontuarioService.listarMeusProntuarios().subscribe({
      next: (prontuarios) => {
        this.construirGrupos(prontuarios);
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Erro ao carregar base clínica.';
        this.isLoading    = false;
        this.cdr.detectChanges();
      }
    });
  }

  construirGrupos(prontuarios: any[]) {
    const mapa = new Map<string, any[]>();
    for (const p of prontuarios) {
      const area = p.area_atendimento || 'Sem Área';
      if (!mapa.has(area)) mapa.set(area, []);
      mapa.get(area)!.push(p);
    }
    this.areasGrupos = Array.from(mapa.entries())
      .sort((a, b) => a[0].localeCompare(b[0], 'pt-BR'))
      .map(([nome, prnts]) => ({ nome, prontuarios: prnts, aberto: true }));
  }

  toggleArea(grupo: AreaGrupo) {
    grupo.aberto = !grupo.aberto;
  }

  get totalProntuarios(): number {
    return this.areasGrupos.reduce((s, g) => s + g.prontuarios.length, 0);
  }

  get gruposFiltrados(): AreaGrupo[] {
    if (!this.termoBusca.trim()) return this.areasGrupos;
    const termo = this.termoBusca.toLowerCase();
    return this.areasGrupos
      .map(g => ({
        ...g,
        prontuarios: g.prontuarios.filter(p =>
          p.nome_paciente?.toLowerCase().includes(termo)     ||
          p.nome_estagiario?.toLowerCase().includes(termo)   ||
          p.numero_prontuario?.toLowerCase().includes(termo)
        )
      }))
      .filter(g => g.prontuarios.length > 0);
  }

  abrirProntuario(prontuario: any) {
    this.router.navigate(['/prontuarios/visao', prontuario._id]);
  }

  formatarData(data: string | null): string {
    if (!data) return '—';
    return new Date(data).toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'Ativo':        return 'bg-green-100 text-green-700';
      case 'Alta':         return 'bg-blue-100  text-blue-700';
      case 'Interrompido': return 'bg-red-100   text-red-700';
      default:             return 'bg-gray-100  text-gray-600';
    }
  }

  getAreaIconClass(nome: string): string {
    if (nome.includes('Neuro'))     return 'bg-purple-100 text-purple-600';
    if (nome.includes('Geriatria')) return 'bg-amber-100  text-amber-600';
    if (nome.includes('Traumato') || nome.includes('Ortoped')) return 'bg-orange-100 text-orange-600';
    if (nome.includes('Cardio'))    return 'bg-red-100    text-red-600';
    if (nome.includes('Saúde'))     return 'bg-teal-100   text-teal-600';
    return                                 'bg-blue-100   text-blue-600';
  }
}
