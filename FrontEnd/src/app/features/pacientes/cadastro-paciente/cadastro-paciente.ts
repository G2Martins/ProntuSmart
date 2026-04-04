import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
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
  private cdr = inject(ChangeDetectorRef); // <-- A MÁGICA PARA DESTRAVAR A TELA AQUI

  pacienteId: string | null = null;
  modoFormulario: 'criar' | 'editar' = 'criar';
  isLoading = false;
  isFetching = false;
  errorMessage = '';

  hoje: string = new Date().toISOString().split('T')[0];
  emailSugestoes: string[] = [];

  areasDisponiveis = [
    "Saúde do Homem e da Mulher", "Geriatria", "Neurologia Adulto", 
    "Neuropediatria", "Ortopedia", "Pediatria"
  ];
  sexosDisponiveis = ["Masculino", "Feminino"];

  // ==========================================
  // VALIDADOR CUSTOMIZADO DE DATA EM TEMPO REAL
  // ==========================================
  validarDataNascimento(control: AbstractControl): ValidationErrors | null {
    if (!control.value) return null;
    
    const partes = control.value.split('-');
    if (partes.length !== 3) return { dataInvalida: true };
    
    const ano = parseInt(partes[0], 10);
    const mes = parseInt(partes[1], 10) - 1;
    const dia = parseInt(partes[2], 10);
    
    const dataDigitada = new Date(ano, mes, dia);
    const dataMinima = new Date(1900, 0, 1);
    
    const hojeObj = new Date();
    hojeObj.setHours(0, 0, 0, 0); // Zera as horas para comparar só o dia justo

    // Se o ano tiver mais de 4 dígitos, for menor que 1900, ou for uma data no futuro: BLOQUEIA!
    if (ano < 1900 || ano > 9999 || dataDigitada < dataMinima || dataDigitada > hojeObj) {
      return { dataInvalida: true };
    }
    
    return null;
  }

  // Vinculamos o novo validador no FormBuilder
  pacienteForm = this.fb.group({
    nome_completo: ['', [Validators.required, Validators.minLength(3)]],
    cpf: ['', [Validators.required, Validators.minLength(14)]],
    data_nascimento: ['', [Validators.required, this.validarDataNascimento.bind(this)]], // <-- Validador Aplicado
    sexo: ['Masculino', Validators.required],
    telefone_contato: ['', [Validators.required, Validators.minLength(14)]],
    email: ['', [Validators.email]],
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

  onCpfInput(event: any) {
    let valor = event.target.value.replace(/\D/g, ''); 
    if (valor.length > 11) valor = valor.slice(0, 11); 

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
    let valor = event.target.value.replace(/\D/g, ''); 
    if (valor.length > 11) valor = valor.slice(0, 11); 

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
    if (valor.length > 1 && !valor.includes('@')) {
      this.emailSugestoes = [`${valor}@gmail.com`, `${valor}@outlook.com`, `${valor}@hotmail.com`];
    } else {
      this.emailSugestoes = []; 
    }
  }

  carregarPacienteParaEdicao() {
    this.isFetching = true;
    this.pacienteService.buscarPorId(this.pacienteId!).subscribe({
      next: (dados) => {
        this.pacienteForm.patchValue(dados);
        this.pacienteForm.get('cpf')?.disable(); 
        this.isFetching = false;
        this.cdr.detectChanges(); // <-- ATUALIZA A TELA (FIM DO LOADING INFINITO)
      },
      error: () => {
        this.errorMessage = 'Erro ao buscar dados do paciente.';
        this.isFetching = false;
        this.cdr.detectChanges(); // <-- ATUALIZA A TELA
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
        this.cdr.detectChanges(); 
      }
    });
  }
}