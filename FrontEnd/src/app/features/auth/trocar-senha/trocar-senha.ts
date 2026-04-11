import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-trocar-senha',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './trocar-senha.html'
})
export class TrocarSenhaComponent {
  fb = inject(FormBuilder);
  authService = inject(AuthService);
  router = inject(Router);

  isLoading = false;
  errorMessage = '';

  // Validador customizado para garantir que as senhas são iguais
  passwordsMatchValidator(control: AbstractControl): ValidationErrors | null {
    const nova = control.get('nova_senha')?.value;
    const conf = control.get('confirmar_senha')?.value;
    return nova === conf ? null : { passwordsMismatch: true };
  }

  trocarForm = this.fb.group({
    senha_temporaria: ['', Validators.required],
    nova_senha: ['', [Validators.required, Validators.minLength(6)]],
    confirmar_senha: ['', Validators.required]
  }, { validators: this.passwordsMatchValidator });

  get f() { return this.trocarForm.controls; }

  onSubmit() {
    if (this.trocarForm.invalid) {
      this.trocarForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const dados = this.trocarForm.value;

    this.authService.efetivarTrocaSenha(dados.senha_temporaria!, dados.nova_senha!).subscribe({
      next: () => {
        // Por questões de segurança, limpamos o token atual (que tinha a flag presa) 
        // e obrigamos o utilizador a entrar de novo com a senha nova.
        alert('Palavra-passe alterada com sucesso! Por favor, faça login com a nova palavra-passe.');
        this.authService.logout();
        this.router.navigate(['/login']);
      },
      error: (erro) => {
        this.isLoading = false;
        this.errorMessage = erro.error?.detail || 'Erro ao alterar a palavra-passe.';
      }
    });
  }
}