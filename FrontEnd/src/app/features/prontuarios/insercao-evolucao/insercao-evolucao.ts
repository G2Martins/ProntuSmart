import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-insercao-evolucao',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink], // RouterLink agora será usado!
  schemas: [CUSTOM_ELEMENTS_SCHEMA], // <-- CORREÇÃO DO ERRO DO ICONIFY AQUI
  templateUrl: './insercao-evolucao.html'
})
export class InsercaoEvolucaoComponent implements OnInit {
  private fb = inject(FormBuilder);
  private router = inject(Router);

  areaProntuario = 'Ortopedia'; 
  isLoading = false;

  evolucaoForm: FormGroup = this.fb.group({
    texto_clinico: ['', [Validators.required, Validators.minLength(20)]],
    medicoes: this.fb.array([]) 
  });

  ngOnInit() {
    this.carregarIndicadoresDaArea();
  }

  get medicoesArray() {
    return this.evolucaoForm.get('medicoes') as FormArray;
  }

  carregarIndicadoresDaArea() {
    const indicadoresBackend = [
      { _id: '1', nome: 'Escala de Dor (EVA)', unidade_medida: 'pontos (0-10)' },
      { _id: '2', nome: 'Força Muscular', unidade_medida: 'grau (0-5)' }
    ];

    indicadoresBackend.forEach(ind => {
      this.medicoesArray.push(this.fb.group({
        indicador_id: [ind._id],
        nome_indicador: [ind.nome],
        unidade: [ind.unidade_medida],
        valor_registrado: ['', Validators.required]
      }));
    });
  }

  onSubmit() {
    if (this.evolucaoForm.invalid) {
      this.evolucaoForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    const dadosParaSalvar = {
      prontuario_id: 'ID_DO_PRONTUARIO',
      ...this.evolucaoForm.value
    };

    console.log("Enviando para o MongoDB:", dadosParaSalvar);
    
    setTimeout(() => { 
      alert('Evolução salva e enviada para o Docente (Status: Pendente de Revisão)!');
      this.router.navigate(['/pacientes']);
    }, 1000);
  }
}