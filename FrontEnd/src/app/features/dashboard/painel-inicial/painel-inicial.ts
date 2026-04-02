import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-painel-inicial',
  standalone: true,
  imports: [CommonModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './painel-inicial.html'
})
export class PainelInicial implements OnInit {
  private authService = inject(AuthService);
  
  perfil: string | null = '';
  saudacao: string = '';

  // --- DADOS FALSOS (MOCK) PARA VISUALIZAÇÃO ---
  // No futuro, isso virá do Backend!

  // Mock Admin
  adminStats = {
    usuariosAtivos: 42,
    areasCadastradas: 6,
    testesConfigurados: 18,
    statusServidor: 'Online'
  };

  // Mock Docente
  docenteStats = {
    estagiariosSupervisionados: 8,
    pacientesAtivos: 34,
    evolucoesPendentesRevisao: 12
  };
  alertasMetas = [
    { paciente: 'Maria Silva', diasEstagnada: 15, area: 'Ortopedia' },
    { paciente: 'João Souza', diasEstagnada: 22, area: 'Neurologia' }
  ];

  // Mock Estagiário
  estagiarioStats = {
    meusPacientes: 5,
    atendimentosHoje: 3,
    evolucoesAtrasadas: 0
  };
  proximosAtendimentos = [
    { paciente: 'Ana Clara', horario: '14:00', area: 'Pediatria' },
    { paciente: 'Carlos Eduardo', horario: '15:30', area: 'Ortopedia' }
  ];

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.definirSaudacao();
  }

  definirSaudacao() {
    const hora = new Date().getHours();
    if (hora < 12) this.saudacao = 'Bom dia';
    else if (hora < 18) this.saudacao = 'Boa tarde';
    else this.saudacao = 'Boa noite';
  }
}