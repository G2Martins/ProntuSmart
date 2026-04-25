import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged, switchMap, of } from 'rxjs';
import { PacienteService }    from '../../../core/services/paciente.service';
import { ProntuarioService }  from '../../../core/services/prontuario.service';
import { CidService }         from '../../../core/services/cid.service';
import { AuthService }        from '../../../core/services/auth.service';

@Component({
  selector: 'app-cadastro-paciente',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './cadastro-paciente.html'
})
export class CadastroPacienteComponent implements OnInit {
  private fb                = inject(FormBuilder);
  private pacienteService   = inject(PacienteService);
  private prontuarioService = inject(ProntuarioService);
  private cidService        = inject(CidService);
  private authService       = inject(AuthService);
  private router            = inject(Router);
  private route             = inject(ActivatedRoute);
  private cdr               = inject(ChangeDetectorRef);

  pacienteId: string | null = null;
  modoFormulario: 'criar' | 'editar' = 'criar';
  perfil       = this.authService.getUserProfile();
  isLoading    = false;
  isFetching   = false;
  errorMessage = '';

  hoje: string = new Date().toISOString().split('T')[0];
  emailSugestoes: string[] = [];

  // Áreas alinhadas com o enum do backend
  areasDisponiveis = [
    "Saúde do Homem e da Mulher",
    "Geriatria",
    "Neurologia Adulto",
    "Neuropediatria",
    "Traumato-Ortopedia",
    "Cardiorrespiratória"
  ];
  sexosDisponiveis = ["Masculino", "Feminino"];

  termoBuscaCid   = '';
  cidsFiltrados: any[] = [];
  cidSelecionado: any  = null;
  buscandoCids         = false;
  private cidSearch$   = new Subject<string>();

  get mostrarTriagem(): boolean {
    return this.modoFormulario === 'criar' && this.perfil === 'Estagiario';
  }

  get mostrarNenhumCidEncontrado(): boolean {
    return this.termoBuscaCid.length >= 2
      && !this.buscandoCids
      && this.cidsFiltrados.length === 0
      && !this.cidSelecionado;
  }

  get mostrarDicaBuscaCid(): boolean {
    return this.termoBuscaCid.length < 2;
  }

  get cidInvalido(): boolean {
    const cidControl = this.pacienteForm.get('cid_id');
    return !!cidControl?.touched && !cidControl.value;
  }

  validarDataNascimento(control: AbstractControl): ValidationErrors | null {
    if (!control.value) return null;
    const partes = control.value.split('-');
    if (partes.length !== 3) return { dataInvalida: true };
    const ano = parseInt(partes[0], 10);
    const mes = parseInt(partes[1], 10) - 1;
    const dia = parseInt(partes[2], 10);
    const dataDigitada = new Date(ano, mes, dia);
    const dataMinima   = new Date(1900, 0, 1);
    const hojeObj      = new Date();
    hojeObj.setHours(0, 0, 0, 0);
    if (ano < 1900 || ano > 9999 || dataDigitada < dataMinima || dataDigitada > hojeObj) {
      return { dataInvalida: true };
    }
    return null;
  }

  pacienteForm = this.fb.group({
    nome_completo:          ['', [Validators.required, Validators.minLength(3)]],
    cpf:                    ['', [Validators.required, Validators.minLength(14)]],
    data_nascimento:        ['', [Validators.required, this.validarDataNascimento.bind(this)]],
    sexo:                   ['Masculino', Validators.required],
    telefone_contato:       ['', [Validators.required, Validators.minLength(14)]],
    email:                  ['', [Validators.email]],
    endereco_resumido:      [''],
    area_atendimento_atual: ['Neurologia Adulto', Validators.required],
    queixa_principal:       [''],
    is_ativo:               [true],
    cid_id:                 ['']
  });

  get f() { return this.pacienteForm.controls; }

  ngOnInit() {
    this.pacienteId = this.route.snapshot.paramMap.get('id');
    if (this.pacienteId) {
      this.modoFormulario = 'editar';
      this.carregarPacienteParaEdicao();
    }

    this.cidSearch$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(termo => {
        if (!termo || termo.length < 2) return of([]);
        this.buscandoCids = true;
        return this.cidService.buscar(termo, 50);
      })
    ).subscribe({
      next: (cids) => {
        this.cidsFiltrados = cids;
        this.buscandoCids  = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.buscandoCids = false;
        this.cdr.detectChanges();
      }
    });
  }

  onBuscaCidChange(termo: string) {
    this.termoBuscaCid = termo;
    this.cidSelecionado = null;
    this.pacienteForm.patchValue({ cid_id: '' });
    this.cidSearch$.next(termo);
  }

  onBuscaCidInput(event: Event) {
    const input = event.target as HTMLInputElement | null;
    this.onBuscaCidChange(input?.value || '');
  }

  selecionarCidDaLista(cid: any) {
    this.cidSelecionado = cid;
    this.termoBuscaCid  = `[${cid.codigo}] ${cid.descricao}`;
    this.cidsFiltrados  = [];
    this.pacienteForm.patchValue({ cid_id: cid._id });
    this.cdr.detectChanges();
  }

  onCpfInput(event: any) {
    let valor = event.target.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.slice(0, 11);
    if (valor.length > 9)      valor = valor.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
    else if (valor.length > 6) valor = valor.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
    else if (valor.length > 3) valor = valor.replace(/(\d{3})(\d{1,3})/, '$1.$2');
    this.pacienteForm.get('cpf')?.setValue(valor, { emitEvent: false });
  }

  onPhoneInput(event: any) {
    let valor = event.target.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.slice(0, 11);
    if (valor.length > 10)     valor = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    else if (valor.length > 6) valor = valor.replace(/(\d{2})(\d{4,5})(\d{0,4})/, '($1) $2-$3');
    else if (valor.length > 2) valor = valor.replace(/(\d{2})(\d{0,5})/, '($1) $2');
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
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Erro ao buscar dados do paciente.';
        this.isFetching   = false;
        this.cdr.detectChanges();
      }
    });
  }

  onSubmit() {
    if (this.mostrarTriagem && !this.pacienteForm.get('cid_id')?.value) {
      this.pacienteForm.get('cid_id')?.markAsTouched();
      this.errorMessage = 'Selecione o diagnóstico principal (CID-10) para abrir o prontuário.';
      return;
    }

    if (this.pacienteForm.invalid) {
      this.pacienteForm.markAllAsTouched();
      return;
    }

    this.isLoading    = true;
    this.errorMessage = '';

    const rawValue = this.pacienteForm.getRawValue();
    const { cid_id, ...dadosPaciente } = rawValue;
    dadosPaciente.email = dadosPaciente.email?.trim() || null;

    if (this.modoFormulario === 'editar') {
      this.pacienteService.atualizar(this.pacienteId!, dadosPaciente).subscribe({
        next: () => {
          this.isLoading = false;
          alert('Paciente atualizado com sucesso!');
          this.router.navigate(['/pacientes']);
        },
        error: (err) => {
          this.isLoading    = false;
          this.errorMessage = err.error?.detail || 'Erro ao atualizar paciente.';
          this.cdr.detectChanges();
        }
      });
    } else {
      // Criar paciente
      this.pacienteService.criar(dadosPaciente).subscribe({
        next: (paciente) => {
          if (this.mostrarTriagem && cid_id) {
            const dadosProntuario = {
              paciente_id:      paciente._id,
              cid_id:           cid_id,
              area_atendimento: rawValue.area_atendimento_atual
            };

            this.prontuarioService.criar(dadosProntuario).subscribe({
              next: (prontuario) => {
                this.isLoading = false;
                this.router.navigate(['/prontuarios/visao', prontuario._id]);
              },
              error: (err) => {
                this.isLoading = false;
                alert('Paciente cadastrado, mas erro ao abrir prontuário: ' + (err.error?.detail || 'Tente pela lista de pacientes.'));
                this.router.navigate(['/pacientes']);
              }
            });
          } else {
            this.isLoading = false;
            alert('Paciente cadastrado com sucesso!');
            this.router.navigate(['/pacientes']);
          }
        },
        error: (err) => {
          this.isLoading    = false;
          this.errorMessage = err.error?.detail || 'Erro ao cadastrar paciente.';
          this.cdr.detectChanges();
        }
      });
    }
  }
}
