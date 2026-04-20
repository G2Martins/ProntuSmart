import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { MetaSmartService } from '../../../core/services/meta-smart.service';
import { IndicadorService } from '../../../core/services/indicador.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';

@Component({
  selector: 'app-insercao-meta-smart',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './insercao-meta-smart.html',
  styleUrl: './insercao-meta-smart.scss'
})
export class InsercaoMetaSmartComponent implements OnInit {
  private fb               = inject(FormBuilder);
  protected router         = inject(Router);
  private route            = inject(ActivatedRoute);
  private metaService      = inject(MetaSmartService);
  private indicadorService = inject(IndicadorService);
  private prontuarioService = inject(ProntuarioService);
  private cdr              = inject(ChangeDetectorRef);

  idProntuario  = '';
  areaProntuario = '';
  indicadores: any[] = [];
  isLoading     = false;
  isFetching    = true;

  hoje = new Date().toISOString().split('T')[0];

  form = this.fb.group({
    indicador_id:          ['', Validators.required],
    problema_relacionado:  [''],
    // SMART
    especifico:            ['', Validators.required],
    criterio_mensuravel:   [''],
    valor_inicial:         [null as number | null, Validators.required],
    valor_alvo:            [null as number | null, Validators.required],
    condicao_execucao:     [''],
    atingivel_resposta:    ['', Validators.required],
    alcancavel:            [''],
    relevante:             ['', Validators.required],
    data_limite:           ['', Validators.required],
    data_reavaliacao:      [''],
  });

  ngOnInit() {
    this.configurarCampoAtingivel();
    this.idProntuario = this.route.snapshot.paramMap.get('id') || '';
    if (this.idProntuario) {
      this.prontuarioService.buscarPorId(this.idProntuario).subscribe({
        next: (pront) => {
          this.areaProntuario = pront.area_atendimento;
          this.carregarIndicadores();
        },
        error: () => { this.isFetching = false; this.cdr.detectChanges(); }
      });
    }
  }

  carregarIndicadores() {
    this.indicadorService.buscarPorArea(this.areaProntuario).subscribe({
      next: (inds) => {
        this.indicadores = inds;
        this.isFetching  = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isFetching = false; this.cdr.detectChanges(); }
    });
  }

  get indicadorSelecionado() {
    const id = this.form.get('indicador_id')?.value;
    return this.indicadores.find(i => i._id === id) || null;
  }

  get mostrarJustificativaAtingivel(): boolean {
    return this.form.get('atingivel_resposta')?.value === 'sim';
  }

  private configurarCampoAtingivel() {
    const respostaCtrl = this.form.get('atingivel_resposta');
    const justificativaCtrl = this.form.get('alcancavel');

    const atualizarValidacao = (resposta: string | null | undefined) => {
      if (resposta === 'sim') {
        justificativaCtrl?.setValidators([Validators.required]);
      } else {
        justificativaCtrl?.clearValidators();
        if (resposta === 'nao') {
          justificativaCtrl?.setValue('', { emitEvent: false });
        }
      }

      justificativaCtrl?.updateValueAndValidity({ emitEvent: false });
    };

    atualizarValidacao(respostaCtrl?.value);
    respostaCtrl?.valueChanges.subscribe((resposta) => atualizarValidacao(resposta));
  }

  onSubmit() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.isLoading = true;

    const v = this.form.value;
    const payload = {
      prontuario_id:        this.idProntuario,
      indicador_id:         v.indicador_id,
      problema_relacionado: v.problema_relacionado,
      especifico:           v.especifico,
      criterio_mensuravel:  v.criterio_mensuravel,
      valor_inicial:        v.valor_inicial,
      valor_alvo:           v.valor_alvo,
      condicao_execucao:    v.condicao_execucao,
      alcancavel:           v.atingivel_resposta === 'sim' ? v.alcancavel : 'N\u00E3o',
      relevante:            v.relevante,
      data_limite:          new Date(v.data_limite!).toISOString(),
      data_reavaliacao:     v.data_reavaliacao ? new Date(v.data_reavaliacao).toISOString() : null,
    };

    this.metaService.criar(payload).subscribe({
      next: () => {
        this.isLoading = false;
        alert('✅ Meta SMART criada com sucesso!');
        this.router.navigate(['/prontuarios/visao', this.idProntuario]);
      },
      error: (err: any) => {
        this.isLoading = false;
        alert(err.error?.detail || 'Erro ao criar meta. Verifique os dados.');
        this.cdr.detectChanges();
      }
    });
  }
}