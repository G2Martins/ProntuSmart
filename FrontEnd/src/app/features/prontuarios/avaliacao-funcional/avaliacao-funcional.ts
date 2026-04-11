import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ProntuarioService } from '../../../core/services/prontuario.service';

@Component({
  selector: 'app-avaliacao-funcional',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './avaliacao-funcional.html',
  styleUrl: './avaliacao-funcional.scss'
})
export class AvaliacaoFuncionalComponent implements OnInit {
  private fb               = inject(FormBuilder);
  protected router         = inject(Router);
  private route            = inject(ActivatedRoute);
  private prontuarioService = inject(ProntuarioService);
  private cdr              = inject(ChangeDetectorRef);

  idProntuario = '';
  isLoading    = false;
  isFetching   = true;
  secaoAtiva   = 1; // wizard de 3 seções

  opSedestacao    = ['Independente', 'Com apoio', 'Dependente'];
  opOrtostatismo  = ['Independente', 'Supervisão', 'Ajuda física', 'Não realiza'];
  opTransferencias = ['Independente', 'Supervisão', 'Ajuda parcial', 'Dependente'];
  opFuncao        = ['Preservada', 'Parcialmente comprometida', 'Comprometida'];
  opEquilibrio    = ['Preservado', 'Alterado'];
  opRiscoQueda    = ['Baixo', 'Moderado', 'Alto'];
  opAVD           = ['I', 'S', 'AP', 'D'];

  form: FormGroup = this.fb.group({
    // Tela 2 — Mobilidade
    sedestacao:         [''],
    ortostatismo:       [''],
    transferencias:     [''],
    realiza_marcha:     [null],
    marcha_dispositivo: [null],
    distancia_tolerada: [''],
    // Função
    funcao_mmss: [''],
    funcao_mmii: [''],
    equilibrio:  [''],
    risco_queda: [''],
    // Sintomas
    dor:                   [null],
    dor_intensidade_local: [''],
    fadiga_funcional:      [null],
    // Cognição
    compreende_comandos:    [null],
    comunicacao_preservada: [null],
    // AVDs
    avd_banho:       [''],
    avd_vestir:      [''],
    avd_higiene:     [''],
    avd_locomocao:   [''],
    avd_alimentacao: [''],
    avd_banheiro:    [''],
    // Participação
    atividade_mais_impactada: [''],
    principal_limitacao:      [''],
    teste_escala_principal:   [''],
    valor_teste_inicial:      [''],
    // Tela 3 — Síntese
    problema_funcional_prioritario: [''],
    atividade_comprometida:         [''],
    impacto_independencia:          [''],
    prioridade_terapeutica:         [''],
  });

  ngOnInit() {
    this.idProntuario = this.route.snapshot.paramMap.get('id') || '';
    if (this.idProntuario) {
      this.prontuarioService.buscarPorId(this.idProntuario).subscribe({
        next: (pront) => {
          // Preenche o form com dados já existentes
          this.form.patchValue(pront);
          this.isFetching = false;
          this.cdr.detectChanges();
        },
        error: () => { this.isFetching = false; this.cdr.detectChanges(); }
      });
    }
  }

  avancar() {
    if (this.secaoAtiva < 3) { this.secaoAtiva++; window.scrollTo({ top: 0, behavior: 'smooth' }); }
  }
  voltar() {
    if (this.secaoAtiva > 1) { this.secaoAtiva--; window.scrollTo({ top: 0, behavior: 'smooth' }); }
  }

  onSubmit() {
    this.isLoading = true;
    const payload = this.form.value;

    this.prontuarioService.atualizarAvaliacao(this.idProntuario, payload).subscribe({
      next: () => {
        this.isLoading = false;
        alert('✅ Avaliação funcional e síntese salvas com sucesso!');
        this.router.navigate(['/prontuarios/visao', this.idProntuario]);
      },
      error: (err: any) => {
        this.isLoading = false;
        alert(err.error?.detail || 'Erro ao salvar avaliação.');
        this.cdr.detectChanges();
      }
    });
  }
}