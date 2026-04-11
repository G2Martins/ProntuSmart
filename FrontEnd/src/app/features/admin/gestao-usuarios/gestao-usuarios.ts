import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
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
export class GestaoUsuariosComponent implements OnInit {
  private fb = inject(FormBuilder);
  private adminService = inject(AdminService);
  private cdr = inject(ChangeDetectorRef);

  usuarios: any[] = [];
  usuarioEditando: any = null;
  isLoading = false;
  isLoadingLista = true;
  successMessage = '';
  errorMessage = '';
  modoFormulario: 'criar' | 'editar' = 'criar';

  areasDisponiveis = [
    "Saúde do Homem e da Mulher",
    "Geriatria",
    "Neurologia Adulto",
    "Neuropediatria",
    "Traumato-Ortopedia",
    "Cardiorrespiratória"
  ];

  usuarioForm = this.fb.group({
    nome_completo:    ['', Validators.required],
    matricula:        ['', Validators.required],
    email:            ['', [Validators.required, Validators.email]],
    senha:            ['', [Validators.required, Validators.minLength(6)]],
    perfil:           ['Estagiario', Validators.required],
    area_atendimento: ['', Validators.required], // obrigatório por padrão (perfil inicial = Estagiário)
    is_ativo:         [true]
  });

  get f() { return this.usuarioForm.controls; }

  ngOnInit() {
    this.carregarUsuarios();

    // Atualiza obrigatoriedade de área conforme o perfil selecionado
    this.usuarioForm.get('perfil')?.valueChanges.subscribe(perfil => {
      const areaCtrl = this.usuarioForm.get('area_atendimento');
      if (perfil === 'Estagiario') {
        areaCtrl?.setValidators([Validators.required]);
      } else {
        areaCtrl?.clearValidators();
        areaCtrl?.setValue('');
      }
      areaCtrl?.updateValueAndValidity();
    });
  }

  carregarUsuarios() {
    this.isLoadingLista = true;
    this.adminService.listarUsuarios().subscribe({
      next: (dados) => {
        this.usuarios = dados;
        this.isLoadingLista = false;
        this.cdr.detectChanges(); // <-- DESTRAVA A TELA AQUI
      },
      error: (erro) => {
        console.error('Erro ao carregar usuários:', erro);
        this.errorMessage = 'Não foi possível carregar a lista de usuários.';
        this.isLoadingLista = false;
        this.cdr.detectChanges(); 
      }
    });
  }

  iniciarEdicao(usuario: any) {
    this.modoFormulario = 'editar';
    this.usuarioEditando = usuario;

    this.usuarioForm.patchValue({
      nome_completo:    usuario.nome_completo,
      matricula:        usuario.matricula,
      email:            usuario.email,
      perfil:           usuario.perfil,
      area_atendimento: usuario.area_atendimento || '',
      is_ativo:         usuario.is_ativo
    });

    // Ajusta validação de área para o perfil do usuário carregado
    const areaCtrl = this.usuarioForm.get('area_atendimento');
    if (usuario.perfil === 'Estagiario') {
      areaCtrl?.setValidators([Validators.required]);
    } else {
      areaCtrl?.clearValidators();
    }
    areaCtrl?.updateValueAndValidity();

    this.usuarioForm.get('senha')?.clearValidators();
    this.usuarioForm.get('senha')?.updateValueAndValidity();

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelarEdicao() {
    this.modoFormulario = 'criar';
    this.usuarioEditando = null;

    this.usuarioForm.reset({ perfil: 'Estagiario', is_ativo: true, area_atendimento: '' });

    this.usuarioForm.get('senha')?.setValidators([Validators.required, Validators.minLength(6)]);
    this.usuarioForm.get('senha')?.updateValueAndValidity();

    // Restaura obrigatoriedade de área (perfil padrão = Estagiário)
    const areaCtrl = this.usuarioForm.get('area_atendimento');
    areaCtrl?.setValidators([Validators.required]);
    areaCtrl?.updateValueAndValidity();

    this.successMessage = '';
    this.errorMessage = '';
  }

  onSubmit() {
    if (this.usuarioForm.invalid) {
      this.usuarioForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    const formValue = this.usuarioForm.value;

    // FLUXO DE CRIAÇÃO (POST)
    if (this.modoFormulario === 'criar') {
      
      const novoUsuario: any = {
        nome_completo: formValue.nome_completo,
        matricula:     formValue.matricula,
        email:         formValue.email,
        senha:         formValue.senha,
        perfil:        formValue.perfil
      };
      if (formValue.perfil === 'Estagiario' && formValue.area_atendimento) {
        novoUsuario.area_atendimento = formValue.area_atendimento;
      }
      
      this.adminService.criarUsuario(novoUsuario).subscribe({
        next: (resposta) => {
          this.isLoading = false;
          this.successMessage = `Sucesso! O usuário ${resposta.nome_completo} foi criado.`;
          this.cancelarEdicao(); 
          this.carregarUsuarios(); 
        },
        error: (erro) => {
          this.isLoading = false;
          this.errorMessage = erro.error?.detail || 'Ocorreu um erro ao criar o usuário.';
          this.cdr.detectChanges(); 
        }
      });
      
    // FLUXO DE EDIÇÃO (PUT)
    } else {
      
      const dadosUpdate: any = {
        nome_completo:    formValue.nome_completo,
        email:            formValue.email,
        perfil:           formValue.perfil,
        is_ativo:         formValue.is_ativo,
        area_atendimento: formValue.perfil === 'Estagiario' ? (formValue.area_atendimento || null) : null
      };

      this.adminService.atualizarUsuario(this.usuarioEditando._id, dadosUpdate).subscribe({
        next: (resposta) => {
          this.isLoading = false;
          this.successMessage = `Sucesso! O usuário ${resposta.nome_completo} foi atualizado.`;
          this.cancelarEdicao();
          this.carregarUsuarios();
        },
        error: (erro) => {
          this.isLoading = false;
          this.errorMessage = erro.error?.detail || 'Ocorreu um erro ao atualizar o usuário.';
          this.cdr.detectChanges(); 
        }
      });
    }
  }

  resetarSenha(usuario: any) {
    if (confirm(`Atenção: Isso irá revogar o acesso atual de ${usuario.nome_completo}. Deseja gerar uma nova senha provisória?`)) {
      this.adminService.resetarSenha(usuario._id).subscribe({
        next: (res: any) => {
          alert(`NOVA SENHA GERADA PARA ${usuario.nome_completo}:\n\n${res.nova_senha}\n\nPor favor, copie e repasse ao usuário. Esta senha não será exibida novamente por segurança.`);
          this.successMessage = `Senha de ${usuario.nome_completo} redefinida com sucesso.`;
          this.cdr.detectChanges();
        },
        error: (erro) => {
          this.errorMessage = erro.error?.detail || 'Erro ao redefinir a senha do usuário.';
          this.cdr.detectChanges();
        }
      });
    }
  }
  
  toggleStatus(usuario: any) {
     const novoStatus = !usuario.is_ativo;
     const txtAcao = novoStatus ? 'REATIVAR' : 'INATIVAR';
     
     if (confirm(`Deseja realmente ${txtAcao} o usuário ${usuario.nome_completo}?`)) {
        this.adminService.atualizarUsuario(usuario._id, { is_ativo: novoStatus }).subscribe({
           next: () => {
              this.successMessage = `Usuário ${usuario.nome_completo} ${novoStatus ? 'ativado' : 'inativado'} com sucesso.`;
              this.carregarUsuarios();
           },
           error: (erro) => {
              this.errorMessage = erro.error?.detail || `Erro ao ${txtAcao} usuário.`;
              this.cdr.detectChanges(); 
           }
        });
     }
  }
}