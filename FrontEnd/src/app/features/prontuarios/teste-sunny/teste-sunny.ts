import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { TesteService } from '../../../core/services/teste.service';

interface ItemSunny {
  ctrl: string;
  label: string;
  descricao: string;
}

interface SecaoSunny {
  titulo: string;
  icone: string;
  itens: ItemSunny[];
}

@Component({
  selector: 'app-teste-sunny',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './teste-sunny.html',
})
export class TesteSunnyComponent implements OnInit {
  private fb            = inject(FormBuilder);
  protected router      = inject(Router);
  private route         = inject(ActivatedRoute);
  private testeService  = inject(TesteService);
  private cdr           = inject(ChangeDetectorRef);

  prontuarioId = '';
  testeId: string | null = null;
  isLoading  = false;
  isFetching = false;

  // Estrutura da Escala de Sunny — avalia funcionalidade global do paciente
  secoes: SecaoSunny[] = [
    {
      titulo: 'Mobilidade Básica',
      icone:  'ph:person-simple-walk-bold',
      itens: [
        { ctrl: 'rolar',           label: 'Rolar no leito',          descricao: 'Capacidade de rolar de decúbito dorsal para lateral' },
        { ctrl: 'sentar',          label: 'Sentar a partir do leito', descricao: 'Sentar sem auxílio externo' },
        { ctrl: 'transferencia',   label: 'Transferência cama/cadeira', descricao: 'Transferir-se com segurança' },
        { ctrl: 'ortostatismo',    label: 'Manutenção de ortostatismo', descricao: 'Manter-se em pé sem apoio' },
      ],
    },
    {
      titulo: 'Marcha e Locomoção',
      icone:  'ph:footprints-bold',
      itens: [
        { ctrl: 'marcha_plana',    label: 'Marcha em superfície plana', descricao: 'Deambular em piso regular' },
        { ctrl: 'marcha_irregular', label: 'Marcha em piso irregular',  descricao: 'Deambular sobre piso desnivelado' },
        { ctrl: 'subir_escadas',   label: 'Subir escadas',             descricao: 'Subir lances com segurança' },
        { ctrl: 'descer_escadas',  label: 'Descer escadas',            descricao: 'Descer lances com segurança' },
      ],
    },
    {
      titulo: 'Função de Membros Superiores',
      icone:  'ph:hand-bold',
      itens: [
        { ctrl: 'alcance',         label: 'Alcance',                    descricao: 'Alcançar objetos acima da cabeça/à frente' },
        { ctrl: 'preensao',        label: 'Preensão palmar',            descricao: 'Segurar objetos com força adequada' },
        { ctrl: 'pinca',           label: 'Pinça fina',                 descricao: 'Realizar pinça digital fina' },
        { ctrl: 'destreza',        label: 'Destreza manual',            descricao: 'Coordenação fina das mãos' },
      ],
    },
    {
      titulo: 'AVDs e Participação',
      icone:  'ph:house-bold',
      itens: [
        { ctrl: 'higiene',         label: 'Higiene pessoal',            descricao: 'Realizar higiene de forma autônoma' },
        { ctrl: 'alimentacao',     label: 'Alimentar-se',               descricao: 'Levar alimento à boca' },
        { ctrl: 'vestir',          label: 'Vestir-se',                  descricao: 'Trocar roupas sem auxílio' },
        { ctrl: 'tarefas_dupla',   label: 'Tarefas de dupla atividade', descricao: 'Manter equilíbrio realizando outra tarefa' },
      ],
    },
  ];

  form: FormGroup;
  observacoes = '';

  // Escala: 0 = Não realiza · 1 = Realiza com auxílio máximo · 2 = Auxílio mínimo · 3 = Independente
  escala = [
    { valor: 0, label: 'Não realiza',        cor: 'red' },
    { valor: 1, label: 'Auxílio máximo',     cor: 'orange' },
    { valor: 2, label: 'Auxílio mínimo',     cor: 'amber' },
    { valor: 3, label: 'Independente',       cor: 'green' },
  ];

  constructor() {
    const controles: any = {};
    this.secoes.forEach(sec => sec.itens.forEach(it => { controles[it.ctrl] = [null, Validators.required]; }));
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
    let total = 0;
    Object.values(this.form.value).forEach(v => total += Number(v) || 0);
    return total;
  }

  get pontuacaoMaxima(): number {
    let n = 0;
    this.secoes.forEach(s => n += s.itens.length);
    return n * 3;
  }

  get percentual(): number {
    if (!this.pontuacaoMaxima) return 0;
    return Math.round((this.pontuacaoTotal / this.pontuacaoMaxima) * 100);
  }

  get interpretacao(): string {
    const p = this.percentual;
    if (p >= 85) return 'Funcionalidade preservada';
    if (p >= 60) return 'Comprometimento leve';
    if (p >= 35) return 'Comprometimento moderado';
    return 'Comprometimento severo';
  }

  classeEscala(cor: string, ativa: boolean): string {
    if (!ativa) return 'border-gray-200 text-gray-500 hover:border-gray-400';
    const map: Record<string, string> = {
      red:    'border-red-500 bg-red-50 text-red-700',
      orange: 'border-orange-500 bg-orange-50 text-orange-700',
      amber:  'border-amber-500 bg-amber-50 text-amber-700',
      green:  'border-green-500 bg-green-50 text-green-700',
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
      tipo:             'Sunny',
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
        alert('✅ Escala de Sunny salva com sucesso!');
        this.router.navigate(['/prontuarios/visao', this.prontuarioId]);
      },
      error: (err) => {
        this.isLoading = false;
        alert(err?.error?.detail || 'Erro ao salvar escala.');
        this.cdr.detectChanges();
      }
    });
  }
}
