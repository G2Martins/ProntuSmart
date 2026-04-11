import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AdminService } from '../../../core/services/admin.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';

@Component({
  selector: 'app-painel-inicial',
  standalone: true,
  imports: [CommonModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './painel-inicial.html'
})
export class PainelInicialComponent implements OnInit {
  private authService      = inject(AuthService);
  private adminService     = inject(AdminService);
  private prontuarioService = inject(ProntuarioService);
  private evolucaoService  = inject(EvolucaoService);
  private cdr              = inject(ChangeDetectorRef);

  perfil:    string | null = '';
  saudacao:  string = '';

  isLoadingStats = true;
  erroStats      = '';

  adminStats: any = {
    usuariosAtivos:    0,
    totalUsuarios:     0,
    areasCadastradas:  0,
    testesConfigurados: 0,
    totalCids:         0,
    totalPacientes:    0,
    statusServidor:    'A verificar...',
    saudeSistema:      null
  };

  docenteStats = {
    estagiariosSupervisionados:  0,
    pacientesAtivos:             0,
    evolucoesPendentesRevisao:   0
  };

  estagiarioStats = { meusPacientes: 0, sessoesRegistradas: 0, pendentesAvaliacao: 0 };
  filaAvaliacao:       any[] = [];
  prontuariosRecentes: any[] = [];

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.definirSaudacao();

    if (this.perfil === 'Administrador') {
      this.carregarEstatisticasAdmin();
    } else if (this.perfil === 'Docente') {
      this.carregarEstatisticasDocente();
    } else if (this.perfil === 'Estagiario') {
      this.carregarEstatisticasEstagiario();
    } else {
      this.isLoadingStats = false;
    }
  }

  carregarEstatisticasAdmin() {
    this.isLoadingStats = true;
    this.erroStats      = '';
    this.adminService.getEstatisticas().subscribe({
      next: (dadosReais: any) => {
        this.adminStats     = dadosReais;
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.erroStats      = 'Não foi possível carregar os dados.';
        this.adminStats.statusServidor = 'Erro de Conexão';
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarEstatisticasDocente() {
    this.isLoadingStats = true;
    this.erroStats      = '';

    // 1. Prontuários do docente
    this.prontuarioService.listarMeusProntuarios().subscribe({
      next: (prontuarios: any[]) => {
        this.docenteStats.pacientesAtivos           = prontuarios.length;
        const estagiariosUnicos                     = new Set(prontuarios.map(p => p.estagiario_id));
        this.docenteStats.estagiariosSupervisionados = estagiariosUnicos.size;
        this.cdr.detectChanges();
      },
      error: () => {
        this.erroStats = 'Erro ao carregar dados clínicos.';
        this.cdr.detectChanges();
      }
    });

    // 2. Evoluções pendentes — chamada independente
    this.evolucaoService.contarPendentesPorDocente().subscribe({
      next: (res) => {
        this.docenteStats.evolucoesPendentesRevisao = res.count;
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarEstatisticasEstagiario() {
    this.isLoadingStats = true;
    this.erroStats = '';
    this.prontuarioService.listarMeusProntuarios().subscribe({
      next: (prontuarios: any[]) => {
        this.estagiarioStats.meusPacientes     = prontuarios.length;
        this.estagiarioStats.sessoesRegistradas = prontuarios.reduce(
          (sum, p) => sum + (p.total_sessoes || 0), 0
        );

        // Pendentes de avaliação = ativos sem avaliação funcional preenchida (sedestacao nula)
        const pendentes = prontuarios.filter(p => p.status === 'Ativo' && !p.sedestacao);
        this.estagiarioStats.pendentesAvaliacao = pendentes.length;
        this.filaAvaliacao = pendentes.slice(0, 5);

        // Prontuários recentes — ordenados por última evolução ou data de criação
        this.prontuariosRecentes = [...prontuarios]
          .sort((a, b) => {
            const ta = a.data_ultima_evolucao
              ? new Date(a.data_ultima_evolucao).getTime()
              : new Date(a.criado_em).getTime();
            const tb = b.data_ultima_evolucao
              ? new Date(b.data_ultima_evolucao).getTime()
              : new Date(b.criado_em).getTime();
            return tb - ta;
          })
          .slice(0, 5);

        this.isLoadingStats = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.erroStats      = 'Não foi possível carregar seus dados clínicos.';
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      }
    });
  }

  definirSaudacao() {
    const hora = new Date().getHours();
    if (hora < 12)      this.saudacao = 'Bom dia';
    else if (hora < 18) this.saudacao = 'Boa tarde';
    else                this.saudacao = 'Boa noite';
  }

  formatarMilhar(valor: number | undefined): string {
    if (valor === undefined || valor === null) return '0';
    if (valor >= 1000) return (valor / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    return valor.toString();
  }

  formatarData(data: string | Date): string {
    if (!data) return '—';
    return new Date(data).toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  }
}