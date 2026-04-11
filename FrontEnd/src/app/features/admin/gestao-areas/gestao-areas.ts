import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AreaService } from '../../../core/services/area.service';

@Component({
  selector: 'app-gestao-areas',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './gestao-areas.html'
})
export class GestaoAreasComponent implements OnInit {
  private fb = inject(FormBuilder);
  private areaService = inject(AreaService);
  private cdr = inject(ChangeDetectorRef);

  areas: any[] = [];
  areaEditando: any = null;
  isLoading = false;
  isLoadingLista = true;
  successMessage = '';
  errorMessage = '';
  modoFormulario: 'criar' | 'editar' = 'criar';

  // Opções para a UI (Ícones Médicos/Físicos e Cores do Tailwind)
  iconesDisponiveis = [
    { icone: 'ph:first-aid-bold', label: 'Primeiros Socorros' },
    { icone: 'ph:bone-bold', label: 'Ortopedia / Ossos' },
    { icone: 'ph:brain-bold', label: 'Neurologia / Cérebro' },
    { icone: 'ph:lungs-bold', label: 'Respiratória / Pulmões' },
    { icone: 'ph:heartbeat-bold', label: 'Cardio / Coração' },
    { icone: 'ph:person-simple-walk-bold', label: 'Reabilitação Motora' },
    { icone: 'ph:baby-bold', label: 'Pediatria' },
    { icone: 'ph:wheelchair-bold', label: 'Acessibilidade' }
  ];

  coresDisponiveis = [
    { valor: 'blue', label: 'Azul', classe: 'bg-blue-500' },
    { valor: 'emerald', label: 'Verde', classe: 'bg-emerald-500' },
    { valor: 'purple', label: 'Roxo', classe: 'bg-purple-500' },
    { valor: 'rose', label: 'Rosa', classe: 'bg-rose-500' },
    { valor: 'orange', label: 'Laranja', classe: 'bg-orange-500' },
    { valor: 'amber', label: 'Amarelo', classe: 'bg-amber-500' },
    { valor: 'cyan', label: 'Ciano', classe: 'bg-cyan-500' }
  ];

  areaForm = this.fb.group({
    nome: ['', Validators.required],
    descricao: [''],
    icone: ['ph:bone-bold', Validators.required],
    cor: ['blue', Validators.required],
    is_ativo: [true]
  });

  get f() { return this.areaForm.controls; }

  ngOnInit() { this.carregarAreas(); }

  carregarAreas() {
    this.isLoadingLista = true;
    this.areaService.listar().subscribe({
      next: (dados) => { this.areas = dados; this.isLoadingLista = false; this.cdr.detectChanges(); },
      error: () => { this.errorMessage = 'Erro ao carregar áreas.'; this.isLoadingLista = false; this.cdr.detectChanges(); }
    });
  }

  iniciarEdicao(area: any) {
    this.modoFormulario = 'editar';
    this.areaEditando = area;
    this.areaForm.patchValue(area);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelarEdicao() {
    this.modoFormulario = 'criar';
    this.areaEditando = null;
    this.areaForm.reset({ icone: 'ph:bone-bold', cor: 'blue', is_ativo: true });
    this.successMessage = ''; this.errorMessage = '';
  }

  onSubmit() {
    if (this.areaForm.invalid) { this.areaForm.markAllAsTouched(); return; }
    this.isLoading = true; this.successMessage = ''; this.errorMessage = '';

    const dados = this.areaForm.value;
    const request = this.modoFormulario === 'criar' 
      ? this.areaService.criar({ nome: dados.nome, descricao: dados.descricao, icone: dados.icone, cor: dados.cor })
      : this.areaService.atualizar(this.areaEditando._id, dados);

    request.subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = `Área "${res.nome}" salva com sucesso!`;
        this.cancelarEdicao();
        this.carregarAreas();
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Erro ao salvar.';
        this.cdr.detectChanges();
      }
    });
  }

  toggleStatus(area: any) {
    const novoStatus = !area.is_ativo;
    this.areaService.atualizar(area._id, { is_ativo: novoStatus }).subscribe({
      next: () => { this.successMessage = `Área atualizada!`; this.carregarAreas(); },
      error: () => { this.errorMessage = `Erro ao alterar status.`; this.cdr.detectChanges(); }
    });
  }

  // Helper para o Tailwind não remover as cores dinâmicas no build (Safe List)
  getBadgeClasses(cor: string): string {
    const mapas: any = {
      'blue': 'bg-blue-100 text-blue-700 border-blue-200',
      'emerald': 'bg-emerald-100 text-emerald-700 border-emerald-200',
      'purple': 'bg-purple-100 text-purple-700 border-purple-200',
      'rose': 'bg-rose-100 text-rose-700 border-rose-200',
      'orange': 'bg-orange-100 text-orange-700 border-orange-200',
      'amber': 'bg-amber-100 text-amber-700 border-amber-200',
      'cyan': 'bg-cyan-100 text-cyan-700 border-cyan-200'
    };
    return mapas[cor] || mapas['blue'];
  }
}