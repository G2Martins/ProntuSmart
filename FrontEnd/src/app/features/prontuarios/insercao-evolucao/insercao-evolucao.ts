import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { IndicadorService } from '../../../core/services/indicador.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';
import { MetaSmartService } from '../../../core/services/meta-smart.service';

@Component({
  selector: 'app-insercao-evolucao',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './insercao-evolucao.html'
})
export class InsercaoEvolucaoComponent implements OnInit {
  private fb                = inject(FormBuilder);
  protected route           = inject(ActivatedRoute);
  protected router          = inject(Router);
  private prontuarioService = inject(ProntuarioService);
  private indicadorService  = inject(IndicadorService);
  private evolucaoService   = inject(EvolucaoService);
  private metaService       = inject(MetaSmartService);
  private cdr               = inject(ChangeDetectorRef);

  idProntuario         = '';
  areaProntuario       = '';
  isLoading            = false;
  isLoadingIndicadores = true;
  temEvolucaoDevolvida = false;

  metasAtivas: any[] = [];

  metaSelecionadaId = '';
  valorAtualMeta    = '';
  houveProgresso    = '';
  condicaoMeta      = '';
  motivoAjuste      = '';
  proximaRevisao    = '';

  evolucaoForm = this.fb.group({
    texto_clinico: ['', [Validators.required, Validators.minLength(10)]],
    medicoes:      this.fb.array([])
  });

  get medicoesArray() { return this.evolucaoForm.get('medicoes') as FormArray; }

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
          this.areaProntuario       = 'Área Indefinida';
          this.isLoadingIndicadores = false;
          this.cdr.detectChanges();
        }
      },
      error: () => {
        this.isLoadingIndicadores = false;
        this.areaProntuario       = 'Erro ao carregar área';
        this.cdr.detectChanges();
      }
    });
  }

  carregarIndicadoresReais() {
    this.isLoadingIndicadores = true;
    this.indicadorService.buscarPorArea(this.areaProntuario).subscribe({
      next: (indicadores: any[]) => {
        while (this.medicoesArray.length) {
          this.medicoesArray.removeAt(0);
        }

        indicadores.forEach((ind: any) => {
          this.medicoesArray.push(this.fb.group({
            indicador_id:     [ind._id],
            nome_indicador:   [ind.nome],
            unidade:          [ind.unidade_medida],
            // ✅ SEM Validators.required — indicadores são OPCIONAIS por sessão.
            // O estagiário preenche apenas os que mensurou. Os vazios são
            // filtrados no onSubmit() antes de enviar ao backend.
            valor_registrado: ['']
          }));
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

  onSubmit() {
    if (this.evolucaoForm.invalid) {
      this.evolucaoForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.cdr.detectChanges();

    const metaSelecionada = this.metasAtivas.find(m => m._id === this.metaSelecionadaId);

    // ✅ Filtra somente as medições efetivamente preenchidas.
    // Campos deixados em branco pelo estagiário são ignorados — evita 422 no backend.
    const medicoesPreenchidas = (this.evolucaoForm.value.medicoes as any[])
      .filter(m =>
        m.valor_registrado !== null &&
        m.valor_registrado !== undefined &&
        String(m.valor_registrado).trim() !== ''
      );

    const dadosParaSalvar: any = {
      prontuario_id:        this.idProntuario,
      texto_clinico:        this.evolucaoForm.value.texto_clinico,
      medicoes:             medicoesPreenchidas,
      meta_id_reavaliada:   this.metaSelecionadaId     || undefined,
      indicador_reavaliado: metaSelecionada?.especifico || undefined,
      valor_atual:          this.valorAtualMeta         || undefined,
      houve_progresso:      this.houveProgresso         || undefined,
      condicao_meta:        this.condicaoMeta           || undefined,
      motivo_ajuste:        this.motivoAjuste           || undefined,
      proxima_revisao:      this.proximaRevisao
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