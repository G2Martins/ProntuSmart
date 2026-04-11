import { Component, inject, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

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
  private router      = inject(Router);
  private cdr         = inject(ChangeDetectorRef); // ← adicionado

  loginForm = this.fb.group({
    matricula: ['', Validators.required],
    senha:     ['', Validators.required]
  });

  errorMessage  = '';
  successMessage = '';
  isLoading     = false;

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading    = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { matricula, senha } = this.loginForm.value;

    this.authService.login(matricula!, senha!).subscribe({
      next: () => {
        this.isLoading = false;

        // Verifica se precisa trocar senha antes de ir ao dashboard
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

        // Distingue os tipos de erro para mensagem clara
        if (err.status === 400 || err.status === 401) {
          this.errorMessage = 'Matrícula ou senha incorretos. Verifique e tente novamente.';
        } else if (err.status === 403) {
          this.errorMessage = 'Usuário inativo. Entre em contato com a administração.';
        } else if (err.status === 0) {
          this.errorMessage = 'Sem conexão com o servidor. Verifique se o backend está rodando.';
        } else {
          this.errorMessage = `Erro inesperado (${err.status}). Tente novamente.`;
        }

        this.cdr.detectChanges(); // ← força render da mensagem de erro
      }
    });
  }
}