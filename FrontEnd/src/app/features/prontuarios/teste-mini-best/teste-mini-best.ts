import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { TesteService } from '../../../core/services/teste.service';

interface ItemBest {
  ctrl: string;
  numero: string;
  label: string;
  descritores: { valor: number; texto: string }[];
}

interface SecaoBest {
  titulo: string;
  icone:  string;
  cor:    string;
  itens:  ItemBest[];
}

@Component({
  selector: 'app-teste-mini-best',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './teste-mini-best.html',
})
export class TesteMiniBestComponent implements OnInit {
  private fb           = inject(FormBuilder);
  protected router     = inject(Router);
  private route        = inject(ActivatedRoute);
  private testeService = inject(TesteService);
  private cdr          = inject(ChangeDetectorRef);

  prontuarioId = '';
  testeId: string | null = null;
  isLoading  = false;
  isFetching = false;

  // Mini-BESTest — 14 itens em 4 seções, escala 0-2 (total 0-28)
  // Adaptado da versão portuguesa europeia
  secoes: SecaoBest[] = [
    {
      titulo: 'Ajustes Posturais Antecipatórios',
      icone:  'ph:person-arms-spread-bold',
      cor:    'blue',
      itens: [
        { ctrl: 'i1_sentado_para_pe', numero: '1', label: 'Sentado para de pé',
          descritores: [
            { valor: 0, texto: 'Incapaz de levantar sem ajuda' },
            { valor: 1, texto: 'Levanta na 1ª tentativa, mas usa as mãos' },
            { valor: 1, texto: 'Levanta sem usar as mãos, mas em mais de uma tentativa' },
            { valor: 2, texto: 'Levanta sem auxílio das mãos em uma só tentativa' },
          ]},
        { ctrl: 'i2_pe_pontas', numero: '2', label: 'Levantar nas pontas dos pés',
          descritores: [
            { valor: 0, texto: 'Incapaz' },
            { valor: 1, texto: 'Mantém <3 segundos ou perde altura' },
            { valor: 2, texto: 'Mantém posição em pontas por ≥3s sem perder altura' },
          ]},
        { ctrl: 'i3_pe_um_pe', numero: '3', label: 'Equilíbrio em apoio unipodal',
          descritores: [
            { valor: 0, texto: 'Incapaz / mantém <2s' },
            { valor: 1, texto: 'Mantém entre 2 e <20s' },
            { valor: 2, texto: 'Mantém ≥20 segundos' },
          ]},
        { ctrl: 'i4_passo_correctivo', numero: '4', label: 'Passo corretivo compensatório anterior/posterior',
          descritores: [
            { valor: 0, texto: 'Cai sem ser amparado' },
            { valor: 1, texto: 'Múltiplos passos para recuperar' },
            { valor: 2, texto: 'Recupera-se sozinho com 1 passo grande' },
          ]},
      ],
    },
    {
      titulo: 'Postura Reativa',
      icone:  'ph:lightning-bold',
      cor:    'orange',
      itens: [
        { ctrl: 'i5_passo_lateral', numero: '5', label: 'Passo corretivo lateral compensatório',
          descritores: [
            { valor: 0, texto: 'Cai ou não consegue dar passo' },
            { valor: 1, texto: 'Múltiplos passos / cruzados' },
            { valor: 2, texto: '1 passo lateral, recupera sozinho' },
          ]},
        { ctrl: 'i6_resposta_anterior', numero: '6', label: 'Resposta a perturbação anterior',
          descritores: [
            { valor: 0, texto: 'Cai ou precisa ser amparado' },
            { valor: 1, texto: 'Múltiplos passos para recuperar' },
            { valor: 2, texto: 'Recupera-se com 1 passo' },
          ]},
        { ctrl: 'i7_resposta_posterior', numero: '7', label: 'Resposta a perturbação posterior',
          descritores: [
            { valor: 0, texto: 'Cai ou precisa ser amparado' },
            { valor: 1, texto: 'Múltiplos passos para recuperar' },
            { valor: 2, texto: 'Recupera-se com 1 passo' },
          ]},
      ],
    },
    {
      titulo: 'Orientação Sensorial',
      icone:  'ph:eye-bold',
      cor:    'purple',
      itens: [
        { ctrl: 'i8_pe_juntos_olhos_abertos', numero: '8', label: 'Pés juntos, olhos abertos, superfície firme',
          descritores: [
            { valor: 0, texto: '<10 segundos / instável' },
            { valor: 1, texto: '30s com inclinações pequenas' },
            { valor: 2, texto: '30s estável' },
          ]},
        { ctrl: 'i9_pe_juntos_olhos_fechados', numero: '9', label: 'Pés juntos, olhos fechados, espuma',
          descritores: [
            { valor: 0, texto: '<10 segundos / cai' },
            { valor: 1, texto: '30s com instabilidade' },
            { valor: 2, texto: '30s estável' },
          ]},
        { ctrl: 'i10_inclinacao', numero: '10', label: 'Inclinação na rampa, olhos fechados',
          descritores: [
            { valor: 0, texto: 'Não tenta ou desvia significativamente' },
            { valor: 1, texto: 'Mantém com pequeno desvio (<5°)' },
            { valor: 2, texto: 'Mantém alinhamento por ≥30s' },
          ]},
      ],
    },
    {
      titulo: 'Marcha Dinâmica',
      icone:  'ph:footprints-bold',
      cor:    'emerald',
      itens: [
        { ctrl: 'i11_alteracao_velocidade', numero: '11', label: 'Marcha — alteração de velocidade',
          descritores: [
            { valor: 0, texto: 'Incapaz de mudar velocidade' },
            { valor: 1, texto: 'Pequena mudança ou usa apoio' },
            { valor: 2, texto: 'Muda velocidade significativamente sem desequilíbrio' },
          ]},
        { ctrl: 'i12_marcha_cabeca', numero: '12', label: 'Marcha com rotação horizontal da cabeça',
          descritores: [
            { valor: 0, texto: 'Perde equilíbrio / não consegue rotacionar' },
            { valor: 1, texto: 'Reduz velocidade e desempenho' },
            { valor: 2, texto: 'Realiza sem alteração da marcha' },
          ]},
        { ctrl: 'i13_pivot_giro', numero: '13', label: 'Marcha com pivot de 180°',
          descritores: [
            { valor: 0, texto: '>5 passos para girar' },
            { valor: 1, texto: '3-4 passos / pés assimétricos' },
            { valor: 2, texto: '≤2 passos, com firmeza' },
          ]},
        { ctrl: 'i14_passar_obstaculos', numero: '14', label: 'Passar por cima de obstáculos',
          descritores: [
            { valor: 0, texto: 'Não consegue passar / acerta o objeto' },
            { valor: 1, texto: 'Reduz velocidade ao passar' },
            { valor: 2, texto: 'Passa sem alteração da marcha' },
          ]},
      ],
    },
  ];

  form: FormGroup;
  observacoes = '';

  escala = [
    { valor: 0, label: 'Severo',   cor: 'red' },
    { valor: 1, label: 'Moderado', cor: 'amber' },
    { valor: 2, label: 'Normal',   cor: 'green' },
  ];

  constructor() {
    const controles: any = {};
    this.secoes.forEach(s => s.itens.forEach(i => { controles[i.ctrl] = [null, Validators.required]; }));
    this.form = this.fb.group(controles);
  }

  ngOnInit() {
    this.prontuarioId = this.route.snapshot.paramMap.get('prontuarioId') || '';
    this.testeId      = this.route.snapshot.paramMap.get('id');

    if (this.testeId) {
      this.isFetching = true;
      this.testeService.buscarPorId(this.testeId).subscribe({
        next: (t) => {
          this.prontuarioId = t.prontuario_id;
          if (t.dados) this.form.patchValue(t.dados);
          this.observacoes = t.observacoes || '';
          this.isFetching = false;
          this.cdr.detectChanges();
        },
        error: () => { this.isFetching = false; this.cdr.detectChanges(); }
      });
    }
  }

  get pontuacaoTotal(): number {
    let t = 0;
    Object.values(this.form.value).forEach(v => t += Number(v) || 0);
    return t;
  }

  get pontuacaoMaxima(): number { return 28; }

  get percentual(): number {
    return Math.round((this.pontuacaoTotal / 28) * 100);
  }

  get interpretacao(): string {
    // Cutoff de risco de queda: ≤19/28 indica risco aumentado
    if (this.pontuacaoTotal >= 24) return 'Equilíbrio funcional preservado';
    if (this.pontuacaoTotal >= 20) return 'Comprometimento leve';
    if (this.pontuacaoTotal >= 15) return 'Risco aumentado de queda';
    return 'Alto risco de queda';
  }

  pontuacaoSecao(secao: SecaoBest): number {
    return secao.itens.reduce((sum, it) => sum + (Number(this.form.get(it.ctrl)?.value) || 0), 0);
  }

  pontuacaoMaximaSecao(secao: SecaoBest): number {
    return secao.itens.length * 2;
  }

  classeEscala(cor: string, ativa: boolean): string {
    if (!ativa) return 'border-gray-200 text-gray-500 hover:border-gray-400';
    const map: Record<string, string> = {
      red:    'border-red-500 bg-red-50 text-red-700',
      amber:  'border-amber-500 bg-amber-50 text-amber-700',
      green:  'border-green-500 bg-green-50 text-green-700',
    };
    return map[cor] || '';
  }

  classeSecaoBg(cor: string): string {
    const map: Record<string, string> = {
      blue:    'bg-blue-50 border-blue-100 text-blue-800',
      orange:  'bg-orange-50 border-orange-100 text-orange-800',
      purple:  'bg-purple-50 border-purple-100 text-purple-800',
      emerald: 'bg-emerald-50 border-emerald-100 text-emerald-800',
    };
    return map[cor] || '';
  }

  classeSecaoIcone(cor: string): string {
    const map: Record<string, string> = {
      blue:    'text-blue-600',
      orange:  'text-orange-600',
      purple:  'text-purple-600',
      emerald: 'text-emerald-600',
    };
    return map[cor] || '';
  }

  onSubmit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.isLoading = true;
    const payload: any = {
      prontuario_id:    this.prontuarioId,
      tipo:             'MiniBest',
      dados:            this.form.value,
      pontuacao_total:  this.pontuacaoTotal,
      pontuacao_maxima: this.pontuacaoMaxima,
      interpretacao:    this.interpretacao,
      observacoes:      this.observacoes,
    };

    const req = this.testeId
      ? this.testeService.atualizar(this.testeId, payload)
      : this.testeService.criar(payload);

    req.subscribe({
      next: () => {
        this.isLoading = false;
        alert('✅ Mini-BESTest salvo com sucesso!');
        this.router.navigate(['/prontuarios/visao', this.prontuarioId]);
      },
      error: (err) => {
        this.isLoading = false;
        alert(err?.error?.detail || 'Erro ao salvar teste.');
        this.cdr.detectChanges();
      }
    });
  }
}
