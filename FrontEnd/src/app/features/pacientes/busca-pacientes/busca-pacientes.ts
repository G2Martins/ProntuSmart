import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms'; // <-- Adicionado Reactive e FormBuilder
import { PacienteService } from '../../../core/services/paciente.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-busca-pacientes',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink], // <-- ReactiveFormsModule adicionado aqui!
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './busca-pacientes.html'
})
export class BuscaPacientesComponent implements OnInit {
   // ... resto do seu código pode continuar igualzinho!
  private pacienteService = inject(PacienteService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  pacientes: any[] = [];
  termoBusca: string = '';
  isLoading = true;
  errorMessage = '';
  perfil: string | null = '';

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.carregarPacientes();
  }

  carregarPacientes() {
    this.isLoading = true;
    this.pacienteService.listar().subscribe({
      next: (dados) => { 
        this.pacientes = dados; 
        this.isLoading = false; 
        this.cdr.detectChanges(); 
      },
      error: () => { 
        this.errorMessage = 'Erro ao carregar base de pacientes.'; 
        this.isLoading = false; 
        this.cdr.detectChanges(); 
      }
    });
  }

  get pacientesFiltrados() {
    if (!this.termoBusca) return this.pacientes;
    const termo = this.termoBusca.toLowerCase();
    return this.pacientes.filter(p => 
      p.nome_completo.toLowerCase().includes(termo) || 
      p.cpf.includes(termo) ||
      p.area_atendimento_atual.toLowerCase().includes(termo)
    );
  }

  abrirTriagem(paciente: any) {
    // Alerta temporário - na Fase 2 isto abrirá o modal de Triagem / Criação de Prontuário
    alert(`🚧 Iniciando Triagem Pedagógica para: ${paciente.nome_completo}\n\nNa Fase 2, o Docente poderá vincular este paciente a um Estagiário, a um CID e a um Indicador aqui!`);
  }
}