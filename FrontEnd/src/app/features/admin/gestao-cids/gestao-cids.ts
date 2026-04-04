import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { CidService } from '../../../core/services/cid.service';

@Component({
  selector: 'app-gestao-cids',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule, RouterLink], // Importante incluir FormsModule para a barra de pesquisa
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './gestao-cids.html'
})
export class GestaoCidsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private cidService = inject(CidService);
  private cdr = inject(ChangeDetectorRef);

  cids: any[] = [];
  termoBusca: string = ''; // Barra de pesquisa em tempo real
  
  cidEditando: any = null;
  isLoading = false;
  isLoadingLista = true;
  successMessage = '';
  errorMessage = '';
  modoFormulario: 'criar' | 'editar' = 'criar';

  cidForm = this.fb.group({
    codigo: ['', [Validators.required, Validators.minLength(3)]],
    descricao: ['', [Validators.required, Validators.minLength(3)]],
    is_ativo: [true]
  });

  get f() { return this.cidForm.controls; }

  ngOnInit() { this.carregarCids(); }

  carregarCids() {
    this.isLoadingLista = true;
    this.cidService.listar().subscribe({
      next: (dados) => { this.cids = dados; this.isLoadingLista = false; this.cdr.detectChanges(); },
      error: () => { this.errorMessage = 'Erro ao carregar CIDs.'; this.isLoadingLista = false; this.cdr.detectChanges(); }
    });
  }

  // Filtro inteligente para a tabela
  get cidsFiltrados() {
    if (!this.termoBusca) return this.cids;
    const termo = this.termoBusca.toLowerCase();
    return this.cids.filter(c => c.codigo.toLowerCase().includes(termo) || c.descricao.toLowerCase().includes(termo));
  }

  iniciarEdicao(cid: any) {
    this.modoFormulario = 'editar';
    this.cidEditando = cid;
    this.cidForm.patchValue(cid);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelarEdicao() {
    this.modoFormulario = 'criar';
    this.cidEditando = null;
    this.cidForm.reset({ is_ativo: true });
    this.successMessage = ''; this.errorMessage = '';
  }

  onSubmit() {
    if (this.cidForm.invalid) { this.cidForm.markAllAsTouched(); return; }
    this.isLoading = true; this.successMessage = ''; this.errorMessage = '';

    const dados = this.cidForm.value;
    const request = this.modoFormulario === 'criar' 
      ? this.cidService.criar({ codigo: dados.codigo, descricao: dados.descricao })
      : this.cidService.atualizar(this.cidEditando._id, dados);

    request.subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = `CID ${res.codigo} salvo com sucesso!`;
        this.cancelarEdicao();
        this.carregarCids();
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Erro ao salvar CID.';
        this.cdr.detectChanges();
      }
    });
  }

  toggleStatus(cid: any) {
    const novoStatus = !cid.is_ativo;
    this.cidService.atualizar(cid._id, { is_ativo: novoStatus }).subscribe({
      next: () => { this.successMessage = `Status atualizado!`; this.carregarCids(); },
      error: () => { this.errorMessage = `Erro ao alterar status.`; this.cdr.detectChanges(); }
    });
  }
}