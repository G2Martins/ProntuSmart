import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
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
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  loginForm = this.fb.group({
    matricula: ['', Validators.required],
    senha: ['', Validators.required]
  });

  errorMessage = '';
  successMessage = ''; // Nova variável para a mensagem de sucesso
  isLoading = false;

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { matricula, senha } = this.loginForm.value;

    this.authService.login(matricula!, senha!).subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = 'Autenticação bem-sucedida! A entrar...';
        
        // Aguarda 1.5 segundos para o utilizador ler a mensagem de sucesso antes de redirecionar
        setTimeout(() => {
          const perfil = this.authService.getUserProfile();
          console.log('Perfil logado:', perfil);
          
          // Redireciona para o Layout base (que contém o dashboard)
          this.router.navigate(['/dashboard']); 
        }, 1500);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Matrícula ou senha incorretos.';
        console.error('Erro no login:', err);
      }
    });
  }
}