import { Component, inject, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './login.html',
})
export class LoginComponent {
  private fb          = inject(FormBuilder);
  private authService = inject(AuthService);
  private http        = inject(HttpClient);
  private router      = inject(Router);
  private cdr         = inject(ChangeDetectorRef);

  abaAtiva: 'login' | 'registrar' = 'login';

  loginForm = this.fb.group({
    matricula: ['', Validators.required],
    senha:     ['', Validators.required]
  });

  registroForm = this.fb.group({
    nome_completo:     ['', [Validators.required, Validators.minLength(3)]],
    matricula:         ['', [Validators.required, Validators.minLength(4)]],
    email:             ['', [Validators.required, Validators.email]],
    senha:             ['', [Validators.required, Validators.minLength(6)]],
    confirmar_senha:   ['', [Validators.required]],
    perfil_solicitado: ['Estagiario', Validators.required],
    area_atendimento:  [''],
    justificativa:     [''],
  });

  areasDisponiveis = [
    'Saúde do Homem e da Mulher',
    'Geriatria',
    'Neurologia Adulto',
    'Neuropediatria',
    'Traumato-Ortopedia',
    'Cardiorrespiratória',
  ];

  errorMessage  = '';
  successMessage = '';
  isLoading     = false;

  trocarAba(aba: 'login' | 'registrar') {
    this.abaAtiva = aba;
    this.errorMessage = '';
    this.successMessage = '';
  }

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading    = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { matricula, senha } = this.loginForm.value;

    this.authService.login(matricula!, senha!).subscribe({
      next: () => {
        this.isLoading = false;
        if (this.authService.needsPasswordChange()) {
          this.router.navigate(['/trocar-senha']);
          return;
        }
        this.successMessage = 'Autenticação bem-sucedida! A entrar...';
        this.cdr.detectChanges();
        setTimeout(() => this.router.navigate(['/dashboard']), 1000);
      },
      error: (err) => {
        this.isLoading = false;
        if (err.status === 400 || err.status === 401) {
          this.errorMessage = 'Matrícula ou senha incorretos. Verifique e tente novamente.';
        } else if (err.status === 403) {
          this.errorMessage = 'Usuário inativo. Entre em contato com a administração.';
        } else if (err.status === 0) {
          this.errorMessage = 'Sem conexão com o servidor. Verifique se o backend está rodando.';
        } else {
          this.errorMessage = `Erro inesperado (${err.status}). Tente novamente.`;
        }
        this.cdr.detectChanges();
      }
    });
  }

  get rf() { return this.registroForm.controls; }

  onRegistrar() {
    this.errorMessage = '';
    this.successMessage = '';

    if (this.registroForm.invalid) {
      this.registroForm.markAllAsTouched();
      return;
    }
    const v = this.registroForm.value;
    if (v.senha !== v.confirmar_senha) {
      this.errorMessage = 'As senhas não coincidem.';
      return;
    }
    if (v.perfil_solicitado === 'Estagiario' && !v.area_atendimento) {
      this.errorMessage = 'Selecione a área de atendimento (obrigatória para Estagiário).';
      return;
    }

    this.isLoading = true;
    const payload: any = {
      nome_completo:     v.nome_completo,
      matricula:         v.matricula,
      email:             v.email,
      senha:             v.senha,
      perfil_solicitado: v.perfil_solicitado,
      justificativa:     v.justificativa || null,
    };
    if (v.perfil_solicitado === 'Estagiario') {
      payload.area_atendimento = v.area_atendimento;
    }

    this.http.post<any>(`${environment.apiUrl}/auth/registrar`, payload).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = res?.message || 'Solicitação enviada! Aguarde aprovação do Administrador.';
        this.registroForm.reset({ perfil_solicitado: 'Estagiario' });
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err?.error?.detail || 'Não foi possível enviar a solicitação.';
        this.cdr.detectChanges();
      }
    });
  }
}
