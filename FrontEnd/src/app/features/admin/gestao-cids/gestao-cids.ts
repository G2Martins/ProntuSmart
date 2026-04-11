import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { CidService } from '../../../core/services/cid.service';
import { AdminService } from '../../../core/services/admin.service';

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
  private adminService = inject(AdminService);

  cids: any[] = [];
  termoBusca: string = ''; // Barra de pesquisa em tempo real
  totalCidsBanco: number = 0;

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

  ngOnInit() {
    this.carregarCids();
    this.carregarEstatisticas(); // <-- CHAME A NOVA FUNÇÃO AQUI
  }

  carregarEstatisticas() {
    this.adminService.getEstatisticas().subscribe({
      next: (res) => {
        if (res && res.totalCids !== undefined) {
          this.totalCidsBanco = res.totalCids;
          this.cdr.detectChanges();
        }
      }
    });
  }

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

  // Transforma 14500 em "14.5k" e 1000 em "1k"
  formatarMilhar(valor: number | undefined): string {
    if (!valor) return '0';

    if (valor >= 1000) {
      // Divide por 1000, fixa 1 casa decimal e remove o ".0" se for exato
      return (valor / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }

    return valor.toString();
  }

  toggleStatus(cid: any) {
    const novoStatus = !cid.is_ativo;
    this.cidService.atualizar(cid._id, { is_ativo: novoStatus }).subscribe({
      next: () => { this.successMessage = `Status atualizado!`; this.carregarCids(); },
      error: () => { this.errorMessage = `Erro ao alterar status.`; this.cdr.detectChanges(); }
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.isLoadingLista = true; // Mostra o loading na tabela
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const jsonAberto = JSON.parse(e.target?.result as string);

        // Mapeia o seu JSON ("Cod_CID" e "Desc_CID") para o formato do nosso BackEnd ("codigo" e "descricao")
        const cidsFormatados = jsonAberto.map((item: any) => ({
          codigo: item.Cod_CID,
          descricao: item.Desc_CID
        }));

        // Envia para o BackEnd
        this.cidService.importarLote(cidsFormatados).subscribe({
          next: (res) => {
            this.successMessage = res.message;
            this.carregarCids(); // Recarrega a tabela atualizada
            this.cdr.detectChanges();
          },
          error: (err) => {
            this.errorMessage = err.error?.detail || 'Erro ao importar o arquivo JSON.';
            this.isLoadingLista = false;
            this.cdr.detectChanges();
          }
        });

      } catch (error) {
        this.errorMessage = "Erro ao ler o arquivo JSON. Verifique se o formato está correto.";
        this.isLoadingLista = false;
        this.cdr.detectChanges();
      }
    };

    reader.readAsText(file);
    event.target.value = ''; // Limpa o input para permitir enviar o mesmo arquivo novamente se der erro
  }
}