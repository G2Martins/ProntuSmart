import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute} from '@angular/router';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { IndicadorService } from '../../../core/services/indicador.service';
import { EvolucaoService } from '../../../core/services/evolucao.service';

@Component({
  selector: 'app-insercao-evolucao',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './insercao-evolucao.html'
})
export class InsercaoEvolucaoComponent implements OnInit {
  private fb = inject(FormBuilder);
  protected router = inject(Router);
  protected route = inject(ActivatedRoute);
  private prontuarioService = inject(ProntuarioService);
  private indicadorService = inject(IndicadorService);
  private evolucaoService = inject(EvolucaoService);
  private cdr = inject(ChangeDetectorRef);

  idProntuario: string = '';
  areaProntuario: string = 'A carregar...';
  isLoading = false;
  isLoadingIndicadores = true;

  evolucaoForm: FormGroup = this.fb.group({
    texto_clinico: ['', [Validators.required, Validators.minLength(20)]],
    medicoes: this.fb.array([])
  });

  ngOnInit() {
    this.idProntuario = this.route.snapshot.paramMap.get('id') || '';

    if (this.idProntuario) {
      this.prontuarioService.buscarPorId(this.idProntuario).subscribe({
        next: (prontuario: any) => {
          this.areaProntuario = prontuario.area_atendimento;
          this.carregarIndicadoresReais();
          this.cdr.detectChanges();
        },
        error: () => {
          this.areaProntuario = 'Área indefinida';
          this.isLoadingIndicadores = false;
          this.cdr.detectChanges();
        }
      });
    }
  }

  get medicoesArray() {
    return this.evolucaoForm.get('medicoes') as FormArray;
  }

  carregarIndicadoresReais() {
    this.isLoadingIndicadores = true;
    this.indicadorService.buscarPorArea(this.areaProntuario).subscribe({
      next: (indicadores: any[]) => {
        indicadores.forEach((ind: any) => {
          this.medicoesArray.push(this.fb.group({
            indicador_id:    [ind._id],
            nome_indicador:  [ind.nome],
            unidade:         [ind.unidade_medida],
            valor_registrado: ['', Validators.required]
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

  onSubmit() {
    if (this.evolucaoForm.invalid) {
      this.evolucaoForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;

    const payload = {
      prontuario_id: this.idProntuario,
      texto_clinico: this.evolucaoForm.value.texto_clinico,
      medicoes: this.evolucaoForm.value.medicoes
    };

    this.evolucaoService.registrar(payload).subscribe({
      next: () => {
        this.isLoading = false;
        alert('✅ Evolução registrada! Status: Pendente de Revisão pelo Docente.');
        this.router.navigate(['/prontuarios/visao', this.idProntuario]);
      },
      error: (err: any) => {
        this.isLoading = false;
        alert(err.error?.detail || 'Erro ao salvar evolução. Tente novamente.');
        this.cdr.detectChanges();
      }
    });
  }
}