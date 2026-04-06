import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router'; // <-- Router adicionado
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { PacienteService } from '../../../core/services/paciente.service';
import { AuthService } from '../../../core/services/auth.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { AdminService } from '../../../core/services/admin.service';
import { CidService } from '../../../core/services/cid.service';

@Component({
  selector: 'app-busca-pacientes',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './busca-pacientes.html'
})
export class BuscaPacientesComponent implements OnInit {
  private pacienteService = inject(PacienteService);
  private authService = inject(AuthService);
  private prontuarioService = inject(ProntuarioService);
  private adminService = inject(AdminService);
  private cidService = inject(CidService);
  private cdr = inject(ChangeDetectorRef);
  private router = inject(Router); // <-- Para navegar de página
  private fb = inject(FormBuilder);

  pacientes: any[] = [];
  termoBusca: string = '';
  isLoading = true;
  errorMessage = '';
  perfil: string | null = '';

  // Variáveis do Modal de Triagem
  mostrarModalTriagem = false;
  pacienteSelecionado: any = null;
  estagiariosDisponiveis: any[] = [];
  cidsDisponiveis: any[] = [];
  areasDisponiveis = ["Saúde do Homem e da Mulher", "Geriatria", "Neurologia Adulto", "Neuropediatria", "Ortopedia", "Pediatria"];
  
  triagemForm = this.fb.group({
    estagiario_id: ['', Validators.required],
    area_atendimento: ['', Validators.required],
    cid_id: ['', Validators.required]
  });

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.carregarPacientes();
    
    // Carrega CIDs e Estagiários na surdina para o Modal estar pronto
    if (this.perfil === 'Docente' || this.perfil === 'Administrador') {
      this.carregarDadosParaTriagem();
    }
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

  carregarDadosParaTriagem() {
    // 1. Busca os estagiários de forma correta e garantida
    this.adminService.listarUsuarios('Estagiário', true).subscribe({
      next: (res: any[]) => {
        // Como já passamos os filtros na API, a resposta já vem limpa
        this.estagiariosDisponiveis = res;
      },
      error: (err) => console.error("Erro ao carregar estagiários:", err)
    });

    // 2. Busca os CIDs
    this.cidService.listar().subscribe({
      next: (res: any[]) => {
        this.cidsDisponiveis = res.filter(c => c.is_ativo);
      },
      error: (err) => console.error("Erro ao carregar CIDs:", err)
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

  // =====================================
  // LÓGICA DO MODAL DE TRIAGEM
  // =====================================

  abrirTriagem(paciente: any) {
    this.pacienteSelecionado = paciente;
    this.mostrarModalTriagem = true;
    this.triagemForm.reset({ area_atendimento: paciente.area_atendimento_atual });
  }

  fecharTriagem() {
    this.mostrarModalTriagem = false;
    this.pacienteSelecionado = null;
  }

  salvarTriagem() {
    if (this.triagemForm.invalid) {
      this.triagemForm.markAllAsTouched();
      return;
    }
    
    // Constrói o objeto exatamente como o Python (ProntuarioCreate) espera
    const dadosProntuario = {
      paciente_id: this.pacienteSelecionado._id,
      estagiario_id: this.triagemForm.value.estagiario_id,
      area_atendimento: this.triagemForm.value.area_atendimento,
      cid_id: this.triagemForm.value.cid_id
    };

    // ENVIA PARA O BANCO DE DADOS
    this.prontuarioService.criarTriagem(dadosProntuario).subscribe({
      next: () => {
        alert(`Triagem concluída! O prontuário foi criado e já está disponível para o Estagiário.`);
        this.fecharTriagem();
      },
      error: (err) => {
        alert(err.error?.detail || 'Erro ao realizar a triagem. Verifique os dados.');
      }
    });
  }

  // =====================================
  // MANIPULAÇÃO DOS DATALISTS (Pesquisa)
  // =====================================

  selecionarEstagiario(event: any) {
    const nomeSelecionado = event.target.value;
    const estagiario = this.estagiariosDisponiveis.find(e => e.nome_completo === nomeSelecionado);
    
    if (estagiario) {
      // Se achou, injeta o ID no formulário reativo
      this.triagemForm.patchValue({ estagiario_id: estagiario._id });
    } else {
      // Se limpou ou digitou errado, limpa o formulário
      this.triagemForm.patchValue({ estagiario_id: '' });
    }
  }

  selecionarCid(event: any) {
    const valorSelecionado = event.target.value;
    // O valor selecionado está no formato "[A00.0] Colera devida a..."
    // Precisamos extrair o código para achar o ID
    const match = valorSelecionado.match(/\[(.*?)\]/); 
    
    if (match) {
      const codigoCid = match[1];
      const cid = this.cidsDisponiveis.find(c => c.codigo === codigoCid);
      if (cid) {
        this.triagemForm.patchValue({ cid_id: cid._id });
        return;
      }
    }
    this.triagemForm.patchValue({ cid_id: '' });
  }

  // =====================================
  // LÓGICA DO BOTÃO ABRIR
  // =====================================

  abrirProntuario(paciente: any) {
    // 1. Pergunta ao BackEnd: "Este paciente tem prontuário ativo?"
    this.prontuarioService.buscarPorPaciente(paciente._id).subscribe({
      next: (prontuario) => {
        // 2. Se tiver, viaja para a tela de visão do Prontuário passando o ID do prontuário!
        this.router.navigate(['/prontuarios/visao', prontuario._id]);
      },
      error: () => {
        // 3. Se não tiver (Erro 404), avisa na tela
        alert(`O paciente ${paciente.nome_completo} ainda não passou por Triagem.\nO Docente precisa clicar em 'Triar' primeiro para gerar o prontuário.`);
      }
    });
  }
}