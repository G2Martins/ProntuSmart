import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AdminService } from '../../../core/services/admin.service';

@Component({
  selector: 'app-gestao-usuarios',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './gestao-usuarios.html'
})
export class GestaoUsuariosComponent {
  private fb = inject(FormBuilder);
  private adminService = inject(AdminService);

  // Criamos o formulário espelhando o nosso UsuarioCreate do FastAPI
  usuarioForm = this.fb.group({
    nome_completo: ['', Validators.required],
    matricula: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    senha: ['', [Validators.required, Validators.minLength(6)]],
    perfil: ['Estagiario', Validators.required] // Por padrão, já vem selecionado como Estagiário
  });

  isLoading = false;
  successMessage = '';
  errorMessage = '';

  onSubmit() {
    if (this.usuarioForm.invalid) {
      this.usuarioForm.markAllAsTouched(); // Mostra os erros em vermelho se o admin tentar enviar vazio
      return;
    }

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    const novoUsuario = this.usuarioForm.value;

    this.adminService.criarUsuario(novoUsuario).subscribe({
      next: (resposta) => {
        this.isLoading = false;
        this.successMessage = `Sucesso! O usuário ${resposta.nome_completo} foi criado no sistema.`;
        this.usuarioForm.reset({ perfil: 'Estagiario' }); // Limpa o formulário para o próximo
      },
      error: (erro) => {
        this.isLoading = false;
        // Pega a mensagem de erro que vem do nosso backend (ex: Matrícula já existe)
        this.errorMessage = erro.error?.detail || 'Ocorreu um erro ao criar o usuário.';
        console.error(erro);
      }
    });
  }

  // Getter de conveniência para validações no HTML
  get f() { return this.usuarioForm.controls; }
}