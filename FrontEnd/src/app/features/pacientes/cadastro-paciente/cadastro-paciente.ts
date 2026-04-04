import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { PacienteService } from '../../../core/services/paciente.service';

@Component({
  selector: 'app-cadastro-paciente',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './cadastro-paciente.html'
})
export class CadastroPacienteComponent implements OnInit {
  private fb = inject(FormBuilder);
  private pacienteService = inject(PacienteService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  pacienteId: string | null = null;
  modoFormulario: 'criar' | 'editar' = 'criar';
  isLoading = false;
  isFetching = false;
  errorMessage = '';

  // Data atual para travar o limite do calendário
  hoje: string = new Date().toISOString().split('T')[0];
  
  // Sugestões dinâmicas de e-mail
  emailSugestoes: string[] = [];

  areasDisponiveis = [
    "Saúde do Homem e da Mulher", "Geriatria", "Neurologia Adulto", 
    "Neuropediatria", "Ortopedia", "Pediatria"
  ];
  sexosDisponiveis = ["Masculino", "Feminino"];

  // Note que atualizamos as validações do CPF e Telefone para acomodar os caracteres da máscara
  pacienteForm = this.fb.group({
    nome_completo: ['', [Validators.required, Validators.minLength(3)]],
    cpf: ['', [Validators.required, Validators.minLength(14)]], // 14 com a máscara
    data_nascimento: ['', Validators.required],
    sexo: ['Masculino', Validators.required],
    telefone_contato: ['', [Validators.required, Validators.minLength(14)]], // 14 ou 15 com a máscara
    email: ['', [Validators.email]], // <-- Valida se tem o @ e formato correto
    endereco_resumido: [''],
    area_atendimento_atual: ['Ortopedia', Validators.required],
    queixa_principal: ['']
  });

  get f() { return this.pacienteForm.controls; }

  ngOnInit() {
    this.pacienteId = this.route.snapshot.paramMap.get('id');
    if (this.pacienteId) {
      this.modoFormulario = 'editar';
      this.carregarPacienteParaEdicao();
    }
  }

  // ==========================================
  // MÁSCARAS E FORMATAÇÕES
  // ==========================================

  onCpfInput(event: any) {
    let valor = event.target.value.replace(/\D/g, ''); // Remove tudo o que não for número
    if (valor.length > 11) valor = valor.slice(0, 11); // Trava em 11 dígitos reais

    // Aplica a máscara 000.000.000-00
    if (valor.length > 9) {
      valor = valor.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
    } else if (valor.length > 6) {
      valor = valor.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
    } else if (valor.length > 3) {
      valor = valor.replace(/(\d{3})(\d{1,3})/, '$1.$2');
    }

    this.pacienteForm.get('cpf')?.setValue(valor, { emitEvent: false });
  }

  onPhoneInput(event: any) {
    let valor = event.target.value.replace(/\D/g, ''); // Remove tudo o que não for número
    if (valor.length > 11) valor = valor.slice(0, 11); // Trava em 11 dígitos reais (DDD + 9 dígitos)

    // Aplica a máscara (00) 00000-0000
    if (valor.length > 10) {
      valor = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (valor.length > 6) {
      valor = valor.replace(/(\d{2})(\d{4,5})(\d{0,4})/, '($1) $2-$3');
    } else if (valor.length > 2) {
      valor = valor.replace(/(\d{2})(\d{0,5})/, '($1) $2');
    }

    this.pacienteForm.get('telefone_contato')?.setValue(valor, { emitEvent: false });
  }

  atualizarSugestoesEmail() {
    const valor = this.pacienteForm.get('email')?.value || '';
    // Se o utilizador começou a digitar mas ainda não colocou o @, sugerimos os domínios
    if (valor.length > 1 && !valor.includes('@')) {
      this.emailSugestoes = [`${valor}@gmail.com`, `${valor}@outlook.com`, `${valor}@hotmail.com`];
    } else {
      this.emailSugestoes = []; // Limpa se já tiver o @ ou estiver vazio
    }
  }

  // ==========================================
  // COMUNICAÇÃO COM A API
  // ==========================================

  carregarPacienteParaEdicao() {
    this.isFetching = true;
    this.pacienteService.buscarPorId(this.pacienteId!).subscribe({
      next: (dados) => {
        this.pacienteForm.patchValue(dados);
        this.pacienteForm.get('cpf')?.disable(); // Impede a alteração do CPF na edição
        this.isFetching = false;
      },
      error: () => {
        this.errorMessage = 'Erro ao buscar dados do paciente.';
        this.isFetching = false;
      }
    });
  }

  onSubmit() {
    if (this.pacienteForm.invalid) {
      this.pacienteForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const dados = this.pacienteForm.getRawValue();
    const request = this.modoFormulario === 'criar'
      ? this.pacienteService.criar(dados)
      : this.pacienteService.atualizar(this.pacienteId!, dados);

    request.subscribe({
      next: () => {
        this.isLoading = false;
        alert(`Paciente ${this.modoFormulario === 'criar' ? 'cadastrado' : 'atualizado'} com sucesso!`);
        this.router.navigate(['/pacientes']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Erro ao processar a requisição.';
      }
    });
  }
}