import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core'; // <-- Importe aqui
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA], // <-- Adicione esta linha! Diz ao Angular para não reclamar da tag <iconify-icon>
  templateUrl: './login.html', // (Confirme se a extensão aqui está .html mesmo, baseado no seu print)
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
  isLoading = false;

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';

    const { matricula, senha } = this.loginForm.value;

    this.authService.login(matricula!, senha!).subscribe({
      next: () => {
        this.isLoading = false;
        console.log('Login efetuado com sucesso!');
        // this.router.navigate(['/dashboard']); 
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Matrícula ou senha incorretos.';
        console.error('Erro no login:', err);
      }
    });
  }
}