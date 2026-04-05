import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AdminService } from '../../../core/services/admin.service';
import { ProntuarioService } from '../../../core/services/prontuario.service'; // <-- NOVO SERVIÇO

@Component({
  selector: 'app-painel-inicial',
  standalone: true,
  imports: [CommonModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './painel-inicial.html'
})
export class PainelInicialComponent implements OnInit {
  private authService = inject(AuthService);
  private adminService = inject(AdminService);
  private prontuarioService = inject(ProntuarioService); // <-- INJETADO
  private cdr = inject(ChangeDetectorRef);

  perfil: string | null = '';
  saudacao: string = '';

  isLoadingStats = true;
  erroStats = '';

  // Stats do Admin
  adminStats: any = {
    usuariosAtivos: 0,
    totalUsuarios: 0,
    areasCadastradas: 0,
    testesConfigurados: 0,
    totalCids: 0,
    totalPacientes: 0,
    statusServidor: 'A verificar...',
    saudeSistema: null
  };

  // Stats do Docente (Agora dinâmico!)
  docenteStats = { 
    estagiariosSupervisionados: 0, 
    pacientesAtivos: 0, 
    evolucoesPendentesRevisao: 0 // Mock temporário até a Fase 3
  };

  // Stats do Estagiário
  estagiarioStats = { meusPacientes: 5, atendimentosHoje: 3, evolucoesAtrasadas: 0 };
  
  alertasMetas: any[] = [];
  proximosAtendimentos: any[] = [];

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.definirSaudacao();

    if (this.perfil === 'Administrador') {
      this.carregarEstatisticasAdmin();
    } else if (this.perfil === 'Docente') {
      this.carregarEstatisticasDocente();
    } else {
      this.isLoadingStats = false; 
    }
  }

  carregarEstatisticasAdmin() {
    this.isLoadingStats = true;
    this.erroStats = '';

    this.adminService.getEstatisticas().subscribe({
      next: (dadosReais: any) => {
        this.adminStats = dadosReais;
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      },
      error: (erro) => {
        console.error('Erro ao buscar estatísticas reais', erro);
        this.erroStats = 'Não foi possível carregar os dados. O servidor pode estar offline.';
        this.adminStats.statusServidor = 'Erro de Conexão';
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      }
    });
  }

  // 👇 NOVA LÓGICA DE DADOS REAIS PARA O DOCENTE 👇
  carregarEstatisticasDocente() {
    this.isLoadingStats = true;
    this.erroStats = '';

    this.prontuarioService.listarMeusProntuarios().subscribe({
      next: (prontuarios: any[]) => {
        // 1. Conta o total de Prontuários (Pacientes em tratamento)
        this.docenteStats.pacientesAtivos = prontuarios.length;
        
        // 2. Extrai apenas os IDs únicos dos estagiários para saber quantos alunos ele supervisiona na prática
        const estagiariosUnicos = new Set(prontuarios.map(p => p.estagiario_id));
        this.docenteStats.estagiariosSupervisionados = estagiariosUnicos.size;

        this.isLoadingStats = false;
        this.cdr.detectChanges();
      },
      error: (erro) => {
        console.error('Erro ao buscar prontuários do docente', erro);
        this.erroStats = 'Erro ao carregar dados clínicos.';
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      }
    });
  }

  definirSaudacao() {
    const hora = new Date().getHours();
    if (hora < 12) this.saudacao = 'Bom dia';
    else if (hora < 18) this.saudacao = 'Boa tarde';
    else this.saudacao = 'Boa noite';
  }

  formatarMilhar(valor: number | undefined): string {
    if (valor === undefined || valor === null) return '0';
    if (valor >= 1000) {
      return (valor / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return valor.toString();
  }
}