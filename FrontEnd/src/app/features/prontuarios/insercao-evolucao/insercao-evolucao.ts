import { ChangeDetectorRef, Component, CUSTOM_ELEMENTS_SCHEMA, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormArray, FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { IndicadorService } from '../../../core/services/indicador.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';
import { MetaSmartService } from '../../../core/services/meta-smart.service';
import { Indicador } from '../../../shared/models/indicador.model';
import {
  aplicarValidadoresLimite,
  descreverLimitesIndicador,
  valorForaDoLimite,
} from '../../../shared/utils/indicador-limites';

@Component({
  selector: 'app-insercao-evolucao',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './insercao-evolucao.html'
})
export class InsercaoEvolucaoComponent implements OnInit {
  private fb = inject(FormBuilder);
  protected route = inject(ActivatedRoute);
  protected router = inject(Router);
  private prontuarioService = inject(ProntuarioService);
  private indicadorService = inject(IndicadorService);
  private evolucaoService = inject(EvolucaoService);
  private metaService = inject(MetaSmartService);
  private cdr = inject(ChangeDetectorRef);

  idProntuario = '';
  areaProntuario = '';
  isLoading = false;
  isLoadingIndicadores = true;
  temEvolucaoDevolvida = false;

  indicadores: Indicador[] = [];
  metasAtivas: any[] = [];

  metaSelecionadaId = '';
  valorAtualMeta: number | null = null;
  houveProgresso = '';
  proximaRevisao = '';

  evolucaoForm = this.fb.group({
    medicoes: this.fb.array([])
  });

  get medicoesArray() { return this.evolucaoForm.get('medicoes') as FormArray; }

  get metaSelecionada(): any | null {
    return this.metasAtivas.find(m => m._id === this.metaSelecionadaId) || null;
  }

  get indicadorMetaSelecionada(): Indicador | null {
    const indicadorId = this.metaSelecionada?.indicador_id;
    return this.indicadores.find(ind => ind._id === indicadorId) || null;
  }

  get descricaoLimitesMetaSelecionada(): string {
    return descreverLimitesIndicador(this.indicadorMetaSelecionada);
  }

  get valorAtualMetaForaDoLimite(): boolean {
    return valorForaDoLimite(this.indicadorMetaSelecionada, this.valorAtualMeta);
  }

  ngOnInit() {
    this.idProntuario = this.route.snapshot.paramMap.get('id') || '';
    if (!this.idProntuario) {
      this.isLoadingIndicadores = false;
      this.cdr.detectChanges();
      return;
    }

    this.prontuarioService.buscarPorId(this.idProntuario).subscribe({
      next: (prontuario: any) => {
        this.areaProntuario = prontuario.area_atendimento || prontuario.area || '';
        this.cdr.detectChanges();

        if (this.areaProntuario) {
          this.carregarIndicadoresReais();
          this.carregarMetasAtivas();
          this.verificarEvolucaoDevolvida();
        } else {
          this.areaProntuario = 'Área Indefinida';
          this.isLoadingIndicadores = false;
          this.cdr.detectChanges();
        }
      },
      error: () => {
        this.isLoadingIndicadores = false;
        this.areaProntuario = 'Erro ao carregar área';
        this.cdr.detectChanges();
      }
    });
  }

  carregarIndicadoresReais() {
    this.isLoadingIndicadores = true;
    this.indicadorService.buscarPorArea(this.areaProntuario).subscribe({
      next: (indicadores: Indicador[]) => {
        this.indicadores = indicadores;

        while (this.medicoesArray.length) {
          this.medicoesArray.removeAt(0);
        }

        indicadores.forEach((ind) => {
          const grupo = this.fb.group({
            indicador_id: [ind._id],
            nome_indicador: [ind.nome],
            unidade: [ind.unidade_medida],
            sem_limitacao_valor: [ind.sem_limitacao_valor],
            limite_minimo: [ind.limite_minimo],
            limite_maximo: [ind.limite_maximo],
            valor_registrado: ['']
          });

          aplicarValidadoresLimite(grupo.get('valor_registrado'), ind);
          this.medicoesArray.push(grupo);
        });

        this.isLoadingIndicadores = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingIndicadores = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarMetasAtivas() {
    this.metaService.listarPorProntuario(this.idProntuario).subscribe({
      next: (metas: any[]) => {
        this.metasAtivas = metas.filter(m =>
          ['Não iniciada', 'Em andamento', 'Parcialmente atingida'].includes(m.status)
        );
        this.cdr.detectChanges();
      },
      error: () => { this.cdr.detectChanges(); }
    });
  }

  verificarEvolucaoDevolvida() {
    this.evolucaoService.listarPorProntuario(this.idProntuario).subscribe({
      next: (evs: any[]) => {
        this.temEvolucaoDevolvida = evs.length > 0 &&
          evs[0].status === 'Ajustes Solicitados';
        this.cdr.detectChanges();
      },
      error: () => { this.cdr.detectChanges(); }
    });
  }

  getDescricaoLimitesMedicao(index: number): string {
    return descreverLimitesIndicador(this.medicoesArray.at(index)?.value);
  }

  onSubmit() {
    if (this.evolucaoForm.invalid || this.valorAtualMetaForaDoLimite) {
      this.evolucaoForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.cdr.detectChanges();

    const metaSelecionada = this.metaSelecionada;
    const medicoesPreenchidas = (this.evolucaoForm.value.medicoes as any[])
      .filter(m =>
        m.valor_registrado !== null &&
        m.valor_registrado !== undefined &&
        String(m.valor_registrado).trim() !== ''
      )
      .map(m => ({
        indicador_id: m.indicador_id,
        nome_indicador: m.nome_indicador,
        unidade: m.unidade,
        valor_registrado: String(m.valor_registrado),
      }));

    const valorAtualStr = (this.valorAtualMeta !== null && this.valorAtualMeta !== undefined)
      ? String(this.valorAtualMeta)
      : undefined;

    const dadosParaSalvar: any = {
      prontuario_id: this.idProntuario,
      medicoes: medicoesPreenchidas,
      meta_id_reavaliada: this.metaSelecionadaId || undefined,
      indicador_reavaliado: metaSelecionada?.especifico || undefined,
      valor_atual: valorAtualStr,
      houve_progresso: this.houveProgresso || undefined,
      proxima_revisao: this.proximaRevisao
        ? new Date(this.proximaRevisao).toISOString() : undefined,
    };

    this.evolucaoService.registrar(dadosParaSalvar).subscribe({
      next: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
        this.router.navigate(['/prontuarios/visao', this.idProntuario]);
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
        alert('Erro ao salvar evolução. Verifique os dados e tente novamente.');
      }
    });
  }
}
