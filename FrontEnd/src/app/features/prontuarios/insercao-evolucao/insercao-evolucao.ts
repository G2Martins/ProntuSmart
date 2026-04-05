import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';

// Injeção correta dos serviços
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { IndicadorService } from '../../../core/services/indicador.service';

@Component({
  selector: 'app-insercao-evolucao',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './insercao-evolucao.html'
})
export class InsercaoEvolucaoComponent implements OnInit {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private route = inject(ActivatedRoute); // Para pegar o ID da URL
  private prontuarioService = inject(ProntuarioService);
  private indicadorService = inject(IndicadorService);

  idProntuario: string = '';
  areaProntuario: string = 'A carregar...'; 
  isLoading = false;

  evolucaoForm: FormGroup = this.fb.group({
    texto_clinico: ['', [Validators.required, Validators.minLength(20)]],
    medicoes: this.fb.array([]) 
  });

  ngOnInit() {
    // Apanha o ID do prontuário da barra de endereço (ex: /prontuarios/evoluir/12345)
    this.idProntuario = this.route.snapshot.paramMap.get('id') || '';

    if (this.idProntuario) {
      // 1. Puxa os dados do prontuário recém-triado
      this.prontuarioService.buscarPorId(this.idProntuario).subscribe({
        next: (prontuario: any) => {
          this.areaProntuario = prontuario.area_atendimento;
          this.carregarIndicadoresReais();
        },
        error: () => {
          this.areaProntuario = 'Área Indefinida (Erro)';
        }
      });
    }
  }

  get medicoesArray() {
    return this.evolucaoForm.get('medicoes') as FormArray;
  }

  carregarIndicadoresReais() {
    // 2. Traz apenas as perguntas (indicadores) que importam para esta área!
    this.indicadorService.buscarPorArea(this.areaProntuario).subscribe({
      next: (indicadores: any[]) => {
        indicadores.forEach((ind: any) => {
          this.medicoesArray.push(this.fb.group({
            indicador_id: [ind._id],
            nome_indicador: [ind.nome],
            unidade: [ind.unidade_medida],
            valor_registrado: ['', Validators.required]
          }));
        });
      },
      error: (err: any) => console.error("Erro ao puxar indicadores", err)
    });
  }

  onSubmit() {
    if (this.evolucaoForm.invalid) {
      this.evolucaoForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    const dadosParaSalvar = {
      prontuario_id: this.idProntuario,
      ...this.evolucaoForm.value
    };

    console.log("Pronto para salvar FatoEvolucao no MongoDB:", dadosParaSalvar);
    
    // (Na Fase 03 criaremos o evolucao.service.ts para salvar isto de verdade)
    setTimeout(() => { 
      alert('Evolução salva e enviada para o Docente (Status: Pendente de Revisão)!');
      this.router.navigate(['/pacientes']);
    }, 1000);
  }
}