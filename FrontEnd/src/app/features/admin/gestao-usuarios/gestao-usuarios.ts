import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
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
  private router = inject(Router); 

  usuarioForm = this.fb.group({
    nome_completo: ['', Validators.required],
    matricula: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    senha: ['', [Validators.required, Validators.minLength(6)]],
    perfil: ['Estagiario', Validators.required]
  });

  isLoading = false;
  successMessage = '';
  errorMessage = '';

  onSubmit() {
    if (this.usuarioForm.invalid) {
      this.usuarioForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    const novoUsuario = this.usuarioForm.value;

    this.adminService.criarUsuario(novoUsuario).subscribe({
      next: (resposta) => {
        this.isLoading = false;
        
        // Mensagem indica que vai redirecionar
        this.successMessage = `Sucesso! O utilizador ${resposta.nome_completo} foi criado. A redirecionar para o painel...`;
        this.usuarioForm.reset({ perfil: 'Estagiario' }); 
        
        // <-- A MÁGICA ACONTECE AQUI: Redireciona após 2 segundos
        setTimeout(() => {
          this.router.navigate(['/dashboard']);
        }, 2000);
      },
      error: (erro) => {
        this.isLoading = false;
        this.errorMessage = erro.error?.detail || 'Ocorreu um erro ao criar o utilizador.';
        console.error(erro);
      }
    });
  }

  get f() { return this.usuarioForm.controls; }
}