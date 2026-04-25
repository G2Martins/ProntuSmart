import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AdminService } from '../../../core/services/admin.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';

@Component({
  selector: 'app-painel-inicial',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
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

  // ── Solicitações de cadastro ───────────────────────────
  solicitacoes: any[] = [];
  isLoadingSolicitacoes = false;
  areasDisponiveis = [
    'Saúde do Homem e da Mulher',
    'Geriatria',
    'Neurologia Adulto',
    'Neuropediatria',
    'Traumato-Ortopedia',
    'Cardiorrespiratória',
  ];

  // Modal aprovar com edição
  modalAprovarAberto = false;
  solicitacaoEmAprovacao: any = null;
  editNome  = '';
  editEmail = '';
  editPerfil = 'Estagiario';
  editArea  = '';
  isAprovando = false;

  // Modal recusar
  modalRecusarAberto = false;
  solicitacaoEmRecusa: any = null;
  motivoRecusa = '';
  isRecusando = false;

  feedbackSolicitacao = '';
  erroSolicitacao = '';

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.definirSaudacao();

    if (this.perfil === 'Administrador') {
      this.carregarEstatisticasAdmin();
      this.carregarSolicitacoes();
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

  // ── Solicitações de cadastro ─────────────────────────────
  carregarSolicitacoes() {
    this.isLoadingSolicitacoes = true;
    this.adminService.listarSolicitacoes('Pendente').subscribe({
      next: (lista) => {
        this.solicitacoes = lista || [];
        this.isLoadingSolicitacoes = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingSolicitacoes = false;
        this.cdr.detectChanges();
      }
    });
  }

  abrirModalAprovar(s: any, modoRapido = false) {
    this.solicitacaoEmAprovacao = s;
    this.editNome   = s.nome_completo;
    this.editEmail  = s.email;
    this.editPerfil = s.perfil_solicitado;
    this.editArea   = s.area_atendimento || '';
    if (modoRapido) {
      this.confirmarAprovacao();
    } else {
      this.modalAprovarAberto = true;
      this.cdr.detectChanges();
    }
  }

  fecharModalAprovar() {
    this.modalAprovarAberto = false;
    this.solicitacaoEmAprovacao = null;
    this.cdr.detectChanges();
  }

  confirmarAprovacao() {
    if (!this.solicitacaoEmAprovacao) return;
    this.isAprovando = true;
    this.erroSolicitacao = '';
    const edits: any = {
      nome_completo:     this.editNome,
      email:             this.editEmail,
      perfil_solicitado: this.editPerfil,
      area_atendimento:  this.editPerfil === 'Estagiario' ? this.editArea : null,
    };
    this.adminService.aprovarSolicitacao(this.solicitacaoEmAprovacao._id, edits).subscribe({
      next: (u) => {
        this.isAprovando = false;
        this.feedbackSolicitacao = `Usuário ${u.nome_completo} aprovado!`;
        this.modalAprovarAberto = false;
        this.solicitacaoEmAprovacao = null;
        this.carregarSolicitacoes();
        setTimeout(() => { this.feedbackSolicitacao = ''; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        this.isAprovando = false;
        this.erroSolicitacao = err?.error?.detail || 'Erro ao aprovar.';
        this.cdr.detectChanges();
      }
    });
  }

  abrirModalRecusar(s: any) {
    this.solicitacaoEmRecusa = s;
    this.motivoRecusa = '';
    this.modalRecusarAberto = true;
    this.cdr.detectChanges();
  }

  fecharModalRecusar() {
    this.modalRecusarAberto = false;
    this.solicitacaoEmRecusa = null;
    this.motivoRecusa = '';
    this.cdr.detectChanges();
  }

  confirmarRecusa() {
    if (!this.solicitacaoEmRecusa || !this.motivoRecusa.trim()) return;
    this.isRecusando = true;
    this.erroSolicitacao = '';
    this.adminService.recusarSolicitacao(this.solicitacaoEmRecusa._id, this.motivoRecusa).subscribe({
      next: () => {
        this.isRecusando = false;
        this.feedbackSolicitacao = 'Solicitação recusada.';
        this.modalRecusarAberto = false;
        this.solicitacaoEmRecusa = null;
        this.carregarSolicitacoes();
        setTimeout(() => { this.feedbackSolicitacao = ''; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        this.isRecusando = false;
        this.erroSolicitacao = err?.error?.detail || 'Erro ao recusar.';
        this.cdr.detectChanges();
      }
    });
  }

  formatarData(data: string | Date): string {
    if (!data) return '—';
    return new Date(data).toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  }
}