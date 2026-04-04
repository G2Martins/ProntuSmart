import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { IndicadorService } from '../../../core/services/indicador.service';
import { Indicador } from '../../../shared/models/indicador.model';

@Component({
  selector: 'app-gestao-indicadores',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './gestao-indicadores.html'
})
export class GestaoIndicadoresComponent implements OnInit {
  private fb = inject(FormBuilder);
  private indicadorService = inject(IndicadorService);
  private cdr = inject(ChangeDetectorRef);

  indicadores: Indicador[] = [];
  indicadorEditando: Indicador | null = null;
  isLoading = false;
  isLoadingLista = true;
  successMessage = '';
  errorMessage = '';
  modoFormulario: 'criar' | 'editar' = 'criar';

  indicadorForm = this.fb.group({
    nome: ['', Validators.required],
    descricao: [''],
    unidade_medida: ['', Validators.required],
    direcao_melhora: ['maior_melhor', Validators.required]
  });

  get f() { return this.indicadorForm.controls; }

  ngOnInit() {
    this.carregarIndicadores();
  }

  carregarIndicadores() {
    this.isLoadingLista = true;
    this.indicadorService.listar().subscribe({
      next: (dados) => {
        this.indicadores = dados;
        this.isLoadingLista = false;
        this.cdr.detectChanges();
      },
      error: (erro) => {
        console.error('Erro ao carregar indicadores:', erro);
        this.errorMessage = 'Não foi possível carregar os indicadores.';
        this.isLoadingLista = false;
        this.cdr.detectChanges();
      }
    });
  }

  iniciarEdicao(indicador: Indicador) {
    this.modoFormulario = 'editar';
    this.indicadorEditando = indicador;
    this.indicadorForm.patchValue({
      nome: indicador.nome,
      descricao: indicador.descricao ?? '',
      unidade_medida: indicador.unidade_medida,
      direcao_melhora: indicador.direcao_melhora
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelarEdicao() {
    this.modoFormulario = 'criar';
    this.indicadorEditando = null;
    this.indicadorForm.reset({ direcao_melhora: 'maior_melhor' });
    this.successMessage = '';
    this.errorMessage = '';
  }

  onSubmit() {
    if (this.indicadorForm.invalid) {
      this.indicadorForm.markAllAsTouched();
      return;
    }
    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';
    const dados = this.indicadorForm.value as any;
    const acao = this.modoFormulario === 'criar'
      ? this.indicadorService.criar(dados)
      : this.indicadorService.atualizar(this.indicadorEditando!._id, dados);
    acao.subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = this.modoFormulario === 'criar'
          ? 'Indicador criado com sucesso!'
          : 'Indicador atualizado com sucesso!';
        this.cancelarEdicao();
        this.carregarIndicadores();
      },
      error: (erro) => {
        this.isLoading = false;
        this.errorMessage = erro.error?.detail || 'Ocorreu um erro. Tente novamente.';
      }
    });
  }

  toggleStatus(indicador: Indicador) {
    const novoStatus = !indicador.is_ativo;
    this.indicadorService.toggleStatus(indicador._id, novoStatus).subscribe({
      next: () => {
        this.successMessage = `Indicador "${indicador.nome}" ${novoStatus ? 'ativado' : 'desativado'} com sucesso.`;
        this.carregarIndicadores();
      },
      error: (erro) => {
        this.errorMessage = erro.error?.detail || 'Erro ao alterar status do indicador.';
      }
    });
  }

  deletar(id: string, nome: string) {
    if (!confirm(`Tem certeza que deseja excluir "${nome}"? Esta ação não pode ser desfeita.`)) return;
    this.indicadorService.deletar(id).subscribe({
      next: () => {
        this.successMessage = `Indicador "${nome}" excluído com sucesso.`;
        this.carregarIndicadores();
      },
      error: (erro) => {
        this.errorMessage = erro.error?.detail || 'Erro ao excluir indicador.';
      }
    });
  }
}