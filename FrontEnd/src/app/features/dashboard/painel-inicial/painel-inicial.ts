import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AdminService } from '../../../core/services/admin.service';

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
  private cdr = inject(ChangeDetectorRef);

  perfil: string | null = '';
  saudacao: string = '';

  isLoadingStats = true;
  erroStats = '';

  adminStats = {
    usuariosAtivos: 0,
    areasCadastradas: 0,
    testesConfigurados: 0,
    statusServidor: 'A verificar...'
  };

  docenteStats = { estagiariosSupervisionados: 8, pacientesAtivos: 34, evolucoesPendentesRevisao: 12 };
  alertasMetas: any[] = [];
  estagiarioStats = { meusPacientes: 5, atendimentosHoje: 3, evolucoesAtrasadas: 0 };
  proximosAtendimentos: any[] = [];

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.definirSaudacao();

    if (this.perfil === 'Administrador') {
      this.carregarEstatisticasAdmin();
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

  definirSaudacao() {
    const hora = new Date().getHours();
    if (hora < 12) this.saudacao = 'Bom dia';
    else if (hora < 18) this.saudacao = 'Boa tarde';
    else this.saudacao = 'Boa noite';
  }
}