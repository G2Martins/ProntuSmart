import { ChangeDetectorRef, Component, CUSTOM_ELEMENTS_SCHEMA, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { IndicadorService } from '../../../core/services/indicador.service';
import { Indicador, IndicadorCreate, IndicadorUpdate } from '../../../shared/models/indicador.model';
import { descreverLimitesIndicador } from '../../../shared/utils/indicador-limites';

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

  readonly unidadeMedidaOptions = [
    { value: '%', label: '%' },
    { value: 'segundos', label: 'segundos' },
    { value: 'grau', label: 'grau' },
    { value: 'graus', label: 'graus' },
    { value: 'pontos', label: 'pontos' },
    { value: 'metros', label: 'metros' },
    { value: 'centímetros', label: 'centímetros' },
    { value: 'outro', label: 'Outra unidade' },
  ];

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
    unidade_medida_opcao: ['', Validators.required],
    unidade_medida_custom: [''],
    direcao_melhora: ['maior_melhor', Validators.required],
    sem_limitacao_valor: [true, Validators.required],
    limite_minimo: [null as number | null],
    limite_maximo: [null as number | null],
    is_ativo: [true]
  });

  get f() { return this.indicadorForm.controls; }

  get usaUnidadeCustom(): boolean {
    return this.indicadorForm.get('unidade_medida_opcao')?.value === 'outro';
  }

  get usaLimites(): boolean {
    return this.indicadorForm.get('sem_limitacao_valor')?.value === false;
  }

  ngOnInit() {
    this.configurarRegrasFormulario();
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

    const usaOpcaoPadrao = this.unidadeMedidaOptions.some(
      opcao => opcao.value !== 'outro' && opcao.value === indicador.unidade_medida,
    );

    this.indicadorForm.patchValue({
      nome: indicador.nome,
      descricao: indicador.descricao ?? '',
      unidade_medida_opcao: usaOpcaoPadrao ? indicador.unidade_medida : 'outro',
      unidade_medida_custom: usaOpcaoPadrao ? '' : indicador.unidade_medida,
      direcao_melhora: indicador.direcao_melhora,
      sem_limitacao_valor: indicador.sem_limitacao_valor ?? true,
      limite_minimo: indicador.limite_minimo ?? null,
      limite_maximo: indicador.limite_maximo ?? null,
      is_ativo: indicador.is_ativo
    });

    this.atualizarValidacaoUnidade();
    this.atualizarValidacaoLimites();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelarEdicao() {
    this.modoFormulario = 'criar';
    this.indicadorEditando = null;
    this.indicadorForm.reset({
      unidade_medida_opcao: '',
      direcao_melhora: 'maior_melhor',
      sem_limitacao_valor: true,
      limite_minimo: null,
      limite_maximo: null,
      is_ativo: true
    });
    this.atualizarValidacaoUnidade();
    this.atualizarValidacaoLimites();
    this.successMessage = '';
    this.errorMessage = '';
  }

  onSubmit() {
    if (this.indicadorForm.invalid) {
      this.indicadorForm.markAllAsTouched();
      return;
    }

    const dados = this.montarPayload();
    if (!dados) return;

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    const acao = this.modoFormulario === 'criar'
      ? this.indicadorService.criar(dados as IndicadorCreate)
      : this.indicadorService.atualizar(this.indicadorEditando!._id, dados as IndicadorUpdate);

    acao.subscribe({
      next: () => {
        this.isLoading = false;
        const mensagemSucesso = this.modoFormulario === 'criar'
          ? 'Indicador criado com sucesso!'
          : 'Indicador atualizado com sucesso!';
        this.cancelarEdicao();
        this.successMessage = mensagemSucesso;
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

  descreverConfiguracaoLimite(indicador: Indicador): string {
    return descreverLimitesIndicador(indicador);
  }

  private configurarRegrasFormulario() {
    this.indicadorForm.get('unidade_medida_opcao')?.valueChanges.subscribe(() => {
      this.atualizarValidacaoUnidade();
    });

    this.indicadorForm.get('sem_limitacao_valor')?.valueChanges.subscribe(() => {
      this.atualizarValidacaoLimites();
    });

    this.atualizarValidacaoUnidade();
    this.atualizarValidacaoLimites();
  }

  private atualizarValidacaoUnidade() {
    const customControl = this.indicadorForm.get('unidade_medida_custom');
    if (!customControl) return;

    if (this.usaUnidadeCustom) {
      customControl.setValidators([Validators.required]);
    } else {
      customControl.clearValidators();
      customControl.setValue('', { emitEvent: false });
    }

    customControl.updateValueAndValidity({ emitEvent: false });
  }

  private atualizarValidacaoLimites() {
    const limiteMinimoControl = this.indicadorForm.get('limite_minimo');
    const limiteMaximoControl = this.indicadorForm.get('limite_maximo');
    if (!limiteMinimoControl || !limiteMaximoControl) return;

    if (!this.usaLimites) {
      limiteMinimoControl.setValue(null, { emitEvent: false });
      limiteMaximoControl.setValue(null, { emitEvent: false });
    }

    limiteMinimoControl.updateValueAndValidity({ emitEvent: false });
    limiteMaximoControl.updateValueAndValidity({ emitEvent: false });
  }

  private montarPayload(): IndicadorCreate | IndicadorUpdate | null {
    const valorUnidade = this.usaUnidadeCustom
      ? this.indicadorForm.get('unidade_medida_custom')?.value?.trim()
      : this.indicadorForm.get('unidade_medida_opcao')?.value?.trim();

    if (!valorUnidade) {
      this.errorMessage = 'Informe a unidade de medida do indicador.';
      this.indicadorForm.get('unidade_medida_custom')?.markAsTouched();
      return null;
    }

    const limiteMinimo = this.normalizarNumero(this.indicadorForm.get('limite_minimo')?.value);
    const limiteMaximo = this.normalizarNumero(this.indicadorForm.get('limite_maximo')?.value);

    if (this.usaLimites && limiteMinimo == null && limiteMaximo == null) {
      this.errorMessage = 'Informe pelo menos um limite ou marque a opção sem limitação.';
      return null;
    }

    if (limiteMinimo != null && limiteMaximo != null && limiteMinimo > limiteMaximo) {
      this.errorMessage = 'O limite mínimo não pode ser maior que o limite máximo.';
      return null;
    }

    return {
      nome: this.indicadorForm.get('nome')?.value?.trim() || '',
      descricao: this.indicadorForm.get('descricao')?.value?.trim() || '',
      unidade_medida: valorUnidade,
      direcao_melhora: this.indicadorForm.get('direcao_melhora')?.value as 'maior_melhor' | 'menor_melhor',
      sem_limitacao_valor: !this.usaLimites,
      limite_minimo: this.usaLimites ? limiteMinimo : null,
      limite_maximo: this.usaLimites ? limiteMaximo : null,
      is_ativo: this.indicadorForm.get('is_ativo')?.value ?? true,
    };
  }

  private normalizarNumero(valor: unknown): number | null {
    if (valor === null || valor === undefined || valor === '') return null;
    const numero = Number(valor);
    return Number.isNaN(numero) ? null : numero;
  }
}
