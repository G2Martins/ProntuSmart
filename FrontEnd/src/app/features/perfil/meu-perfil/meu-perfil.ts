import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';
import { AdminService } from '../../../core/services/admin.service';

interface StatCard {
  icone: string;
  label: string;
  valor: string | number;
  cor: string;
}

@Component({
  selector: 'app-meu-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './meu-perfil.html'
})
export class MeuPerfilComponent implements OnInit {
  private authService       = inject(AuthService);
  private prontuarioService = inject(ProntuarioService);
  private evolucaoService   = inject(EvolucaoService);
  private adminService      = inject(AdminService);
  private fb                = inject(FormBuilder);
  private cdr               = inject(ChangeDetectorRef);

  perfil      = this.authService.getUserProfile();
  nomeLocal   = this.authService.getUserName();

  isLoadingPerfil = true;
  erroPerfil      = '';
  usuario: any    = null;

  isLoadingStats = true;
  stats: StatCard[] = [];

  mostrarFormSenha = false;
  isAlterandoSenha = false;
  erroSenha        = '';
  sucessoSenha     = '';

  senhaForm = this.fb.group(
    {
      senhaAtual:     ['', [Validators.required]],
      novaSenha:      ['', [Validators.required, Validators.minLength(8)]],
      confirmarSenha: ['', [Validators.required]]
    },
    {
      validators: (group: AbstractControl) => {
        const nova      = group.get('novaSenha')?.value;
        const confirmar = group.get('confirmarSenha')?.value;
        return nova === confirmar ? null : { senhasDiferentes: true };
      }
    }
  );

  ngOnInit() {
    this.carregarPerfil();
  }

  carregarPerfil() {
    this.isLoadingPerfil = true;
    this.erroPerfil      = '';
    this.authService.getMe().subscribe({
      next: (usuario) => {
        this.usuario         = usuario;
        this.isLoadingPerfil = false;
        this.carregarStats();
        this.cdr.detectChanges();
      },
      error: () => {
        this.erroPerfil      = 'Não foi possível carregar seus dados.';
        this.isLoadingPerfil = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarStats() {
    this.isLoadingStats = true;

    if (this.perfil === 'Estagiario') {
      this.prontuarioService.listarMeusProntuarios().subscribe({
        next: (prontuarios: any[]) => {
          const sessoes   = prontuarios.reduce((s, p) => s + (p.total_sessoes || 0), 0);
          const pendentes = prontuarios.filter(p => p.status === 'Ativo' && !p.sedestacao).length;
          this.stats = [
            { icone: 'ph:users-three-bold',      label: 'Prontuários Vinculados',  valor: prontuarios.length, cor: 'blue'   },
            { icone: 'ph:clipboard-text-bold',   label: 'Sessões Registradas',     valor: sessoes,            cor: 'emerald'},
            { icone: 'ph:hourglass-medium-bold', label: 'Pendentes de Avaliação',  valor: pendentes,          cor: 'orange' },
          ];
          this.isLoadingStats = false;
          this.cdr.detectChanges();
        },
        error: () => { this.isLoadingStats = false; this.cdr.detectChanges(); }
      });

    } else if (this.perfil === 'Docente') {
      this.prontuarioService.listarMeusProntuarios().subscribe({
        next: (prontuarios: any[]) => {
          const estagiarios = new Set(prontuarios.map(p => p.estagiario_id)).size;
          this.stats = [
            { icone: 'ph:users-three-bold', label: 'Pacientes Supervisionados', valor: prontuarios.length, cor: 'blue'   },
            { icone: 'ph:student-bold',     label: 'Estagiários Vinculados',    valor: estagiarios,        cor: 'purple' },
          ];
          this.evolucaoService.contarPendentesPorDocente().subscribe({
            next: (res) => {
              this.stats.push({ icone: 'ph:signature-bold', label: 'Evoluções p/ Revisão', valor: res.count, cor: 'orange' });
              this.isLoadingStats = false;
              this.cdr.detectChanges();
            },
            error: () => { this.isLoadingStats = false; this.cdr.detectChanges(); }
          });
          this.cdr.detectChanges();
        },
        error: () => { this.isLoadingStats = false; this.cdr.detectChanges(); }
      });

    } else if (this.perfil === 'Administrador') {
      this.adminService.getEstatisticas().subscribe({
        next: (dados: any) => {
          this.stats = [
            { icone: 'ph:users-bold',      label: 'Usuários Ativos',          valor: dados.usuariosAtivos    || 0, cor: 'blue'   },
            { icone: 'ph:heartbeat-bold',  label: 'Áreas Clínicas',           valor: dados.areasCadastradas  || 0, cor: 'emerald'},
            { icone: 'ph:chart-line-bold', label: 'Indicadores Cadastrados',  valor: dados.testesConfigurados || 0, cor: 'purple' },
          ];
          this.isLoadingStats = false;
          this.cdr.detectChanges();
        },
        error: () => { this.isLoadingStats = false; this.cdr.detectChanges(); }
      });

    } else {
      this.isLoadingStats = false;
    }
  }

  alterarSenha() {
    if (this.senhaForm.invalid) return;
    this.isAlterandoSenha = true;
    this.erroSenha        = '';
    this.sucessoSenha     = '';

    const { senhaAtual, novaSenha } = this.senhaForm.value;
    this.authService.efetivarTrocaSenha(senhaAtual!, novaSenha!).subscribe({
      next: () => {
        this.sucessoSenha     = 'Senha alterada com sucesso!';
        this.isAlterandoSenha = false;
        this.senhaForm.reset();
        this.mostrarFormSenha = false;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.erroSenha        = err?.error?.detail || 'Não foi possível alterar a senha.';
        this.isAlterandoSenha = false;
        this.cdr.detectChanges();
      }
    });
  }

  getInitials(): string {
    const nome = this.usuario?.nome_completo || this.nomeLocal || '';
    if (!nome) return (this.perfil || '?')[0].toUpperCase();
    const parts = nome.trim().split(' ').filter((p: string) => p.length > 0);
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  getAvatarGradient(): string {
    switch (this.perfil) {
      case 'Administrador': return 'from-orange-500 to-red-500';
      case 'Docente':       return 'from-purple-500 to-indigo-600';
      default:              return 'from-blue-500 to-cyan-600';
    }
  }

  getBannerGradient(): string {
    switch (this.perfil) {
      case 'Administrador': return 'from-orange-500 to-red-600';
      case 'Docente':       return 'from-purple-600 to-indigo-700';
      default:              return 'from-blue-600 to-cyan-600';
    }
  }

  getPerfilBadgeClass(): string {
    switch (this.perfil) {
      case 'Administrador': return 'bg-orange-100 text-orange-700 border border-orange-200';
      case 'Docente':       return 'bg-purple-100 text-purple-700 border border-purple-200';
      default:              return 'bg-blue-100 text-blue-700 border border-blue-200';
    }
  }

  getStatIconClass(cor: string): string {
    const map: Record<string, string> = {
      blue:    'bg-blue-50 text-blue-600',
      emerald: 'bg-emerald-50 text-emerald-600',
      purple:  'bg-purple-50 text-purple-600',
      orange:  'bg-orange-50 text-orange-500',
    };
    return map[cor] || 'bg-gray-50 text-gray-600';
  }

  formatarDataCadastro(data: string): string {
    if (!data) return '—';
    return new Date(data).toLocaleDateString('pt-BR', {
      day: '2-digit', month: 'long', year: 'numeric'
    });
  }
}
