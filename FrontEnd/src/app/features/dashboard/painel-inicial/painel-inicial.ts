import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AdminService } from '../../../core/services/admin.service'; // <-- Importe o serviço

@Component({
  selector: 'app-painel-inicial',
  standalone: true,
  imports: [CommonModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './painel-inicial.html'
})
export class PainelInicialComponent implements OnInit {
  private authService = inject(AuthService);
  private adminService = inject(AdminService); // <-- Injete o serviço
  
  perfil: string | null = '';
  saudacao: string = '';

  // DADOS REAIS DO ADMIN (Inicializados a zero até a API responder)
  adminStats = {
    usuariosAtivos: 0,
    areasCadastradas: 0,
    testesConfigurados: 0,
    statusServidor: 'A carregar...'
  };

  // ... (Pode manter os mocks do Docente e Estagiário por agora, até chegarmos neles)
  docenteStats = { estagiariosSupervisionados: 8, pacientesAtivos: 34, evolucoesPendentesRevisao: 12 };
  alertasMetas: any[] = [];
  estagiarioStats = { meusPacientes: 5, atendimentosHoje: 3, evolucoesAtrasadas: 0 };
  proximosAtendimentos: any[] = [];

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.definirSaudacao();
    
    // SE FOR ADMINISTRADOR, BUSCA OS DADOS REAIS!
    if (this.perfil === 'Administrador') {
      this.carregarEstatisticasAdmin();
    }
  }

  carregarEstatisticasAdmin() {
    this.adminService.getEstatisticas().subscribe({
      next: (dadosReais) => {
        this.adminStats = dadosReais; // Atualiza a interface magicamente
      },
      error: (erro) => {
        console.error('Erro ao buscar estatísticas reais', erro);
        this.adminStats.statusServidor = 'Erro de Conexão';
      }
    });
  }

  definirSaudacao() {
    const hora = new Date().getHours();
    if (hora < 12) this.saudacao = 'Bom dia';
    else if (hora < 18) this.saudacao = 'Boa tarde';
    else this.saudacao = 'Boa noite';
  }
}