import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { RelatorioService } from '../../../core/services/relatorio.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { PacienteService } from '../../../core/services/paciente.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-gerar-relatorio',
  standalone: true,
  imports: [CommonModule, FormsModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './gerar-relatorio.html'
})
export class GerarRelatorioComponent implements OnInit {
  private route             = inject(ActivatedRoute);
  protected router          = inject(Router);
  private relatorioService  = inject(RelatorioService);
  private prontuarioService = inject(ProntuarioService);
  private pacienteService   = inject(PacienteService);
  private authService       = inject(AuthService);
  private sanitizer         = inject(DomSanitizer);
  private cdr               = inject(ChangeDetectorRef);

  perfil = this.authService.getUserProfile();

  modo: 'criar' | 'visualizar' = 'criar';
  prontuarioId: string | null = null;
  relatorioId:  string | null = null;

  prontuario: any = null;
  paciente:   any = null;
  relatorio:  any = null;

  isLoading       = true;
  isSalvando      = false;
  isAssinando     = false;
  errorMessage    = '';
  successMessage  = '';

  // Formulário do relatório
  tipoSelecionado: 'Padrao' | 'Completo' = 'Padrao';
  docenteSelecionado = '';
  docentesDisponiveis: any[] = [];
  isLoadingDocentes = false;
  form = {
    diagnostico_clinico:           '',
    queixa_principal:              '',
    diagnostico_fisioterapeutico:  '',
    objetivos_tratamento:          '',
    atividades_realizadas:         '',
    observacoes_evolucao:          '',
    consideracoes_finais:          '',
  };

  // Preview do PDF
  pdfUrl: SafeResourceUrl | null = null;
  isLoadingPdf = false;

  // Modal de assinatura
  modalAssinaturaAberto = false;
  senhaAssinatura       = '';

  ngOnInit() {
    this.prontuarioId = this.route.snapshot.paramMap.get('prontuarioId');
    this.relatorioId  = this.route.snapshot.paramMap.get('id');

    if (this.relatorioId) {
      this.modo = 'visualizar';
      this.carregarRelatorio();
    } else if (this.prontuarioId) {
      this.modo = 'criar';
      this.carregarProntuario();
    } else {
      this.errorMessage = 'Parâmetros inválidos.';
      this.isLoading = false;
    }
  }

  // ── Carga em modo criar ────────────────────────────────────
  carregarProntuario() {
    if (!this.prontuarioId) return;
    this.isLoading = true;
    this.prontuarioService.buscarPorId(this.prontuarioId).subscribe({
      next: (pront) => {
        this.prontuario = pront;
        // Sugestões úteis
        if (pront.problema_funcional_prioritario) {
          this.form.objetivos_tratamento = `Abordar ${pront.problema_funcional_prioritario.toLowerCase()}, ${pront.prioridade_terapeutica || ''}`.trim();
        }

        // Carrega lista de docentes disponíveis para assinar (apenas no relatório padrão)
        this.carregarDocentesDisponiveis();

        if (pront.paciente_id) {
          this.pacienteService.buscarPorId(pront.paciente_id).subscribe({
            next: (pac) => {
              this.paciente = pac;
              this.isLoading = false;
              this.cdr.detectChanges();
            }
          });
        } else {
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      },
      error: () => {
        this.errorMessage = 'Erro ao carregar prontuário.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarDocentesDisponiveis() {
    if (!this.prontuarioId) return;
    this.isLoadingDocentes = true;
    this.relatorioService.listarDocentesDisponiveis(this.prontuarioId).subscribe({
      next: (docs) => {
        this.docentesDisponiveis = docs || [];
        // Pré-seleciona o primeiro docente revisor (se houver)
        const revisor = this.docentesDisponiveis.find(d => d.ja_revisou);
        if (revisor) {
          this.docenteSelecionado = revisor._id;
        } else if (this.docentesDisponiveis.length > 0) {
          this.docenteSelecionado = this.docentesDisponiveis[0]._id;
        }
        this.isLoadingDocentes = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingDocentes = false;
        this.cdr.detectChanges();
      }
    });
  }

  // ── Carga em modo visualizar ──────────────────────────────
  carregarRelatorio() {
    if (!this.relatorioId) return;
    this.isLoading = true;
    this.relatorioService.buscarPorId(this.relatorioId).subscribe({
      next: (rel) => {
        this.relatorio = rel;
        this.tipoSelecionado = rel.tipo;
        this.form = {
          diagnostico_clinico:          rel.diagnostico_clinico          || '',
          queixa_principal:             rel.queixa_principal             || '',
          diagnostico_fisioterapeutico: rel.diagnostico_fisioterapeutico || '',
          objetivos_tratamento:         rel.objetivos_tratamento         || '',
          atividades_realizadas:        rel.atividades_realizadas        || '',
          observacoes_evolucao:         rel.observacoes_evolucao         || '',
          consideracoes_finais:         rel.consideracoes_finais         || '',
        };
        this.prontuarioId = rel.prontuario_id;

        // Carrega prontuário e paciente também (para o cabeçalho)
        this.prontuarioService.buscarPorId(rel.prontuario_id).subscribe({
          next: (pront) => {
            this.prontuario = pront;
            if (pront.paciente_id) {
              this.pacienteService.buscarPorId(pront.paciente_id).subscribe({
                next: (pac) => {
                  this.paciente = pac;
                  this.isLoading = false;
                  this.carregarPreviewPdf();
                  this.cdr.detectChanges();
                }
              });
            } else {
              this.isLoading = false;
              this.cdr.detectChanges();
            }
          }
        });
      },
      error: () => {
        this.errorMessage = 'Erro ao carregar relatório.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  // ── Salvar / Atualizar rascunho ───────────────────────────
  salvarRascunho() {
    if (this.modo === 'criar') {
      this.criarRascunho();
    } else if (this.relatorio?.status === 'Rascunho') {
      this.atualizarRascunho();
    }
  }

  criarRascunho() {
    if (!this.prontuarioId) return;

    // Validação local: tipo padrão exige docente
    if (this.tipoSelecionado === 'Padrao' && !this.docenteSelecionado) {
      this.errorMessage = 'Selecione o preceptor que assinará o relatório padrão.';
      return;
    }

    this.isSalvando = true;
    this.errorMessage = '';
    const payload: any = {
      prontuario_id: this.prontuarioId,
      tipo: this.tipoSelecionado,
      ...this.form,
    };
    if (this.tipoSelecionado === 'Padrao') {
      payload.docente_id = this.docenteSelecionado;
    }
    this.relatorioService.criar(payload).subscribe({
      next: (rel) => {
        this.relatorio = rel;
        this.relatorioId = rel._id;
        this.modo = 'visualizar';
        this.isSalvando = false;
        this.successMessage = 'Rascunho criado com sucesso!';
        this.carregarPreviewPdf();
        // Atualiza URL sem recarregar
        this.router.navigate(['/relatorios/visualizar', rel._id], { replaceUrl: true });
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isSalvando = false;
        this.errorMessage = err.error?.detail || 'Erro ao criar rascunho.';
        this.cdr.detectChanges();
      }
    });
  }

  atualizarRascunho() {
    if (!this.relatorioId) return;
    this.isSalvando = true;
    this.errorMessage = '';
    this.relatorioService.atualizar(this.relatorioId, this.form).subscribe({
      next: (rel) => {
        this.relatorio = rel;
        this.isSalvando = false;
        this.successMessage = 'Rascunho atualizado!';
        this.carregarPreviewPdf();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isSalvando = false;
        this.errorMessage = err.error?.detail || 'Erro ao atualizar.';
        this.cdr.detectChanges();
      }
    });
  }

  // ── Preview do PDF ────────────────────────────────────────
  carregarPreviewPdf() {
    if (!this.relatorioId) return;
    this.isLoadingPdf = true;
    this.relatorioService.baixarPdf(this.relatorioId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        this.pdfUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
        this.isLoadingPdf = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingPdf = false;
        this.cdr.detectChanges();
      }
    });
  }

  baixarPdfDireto() {
    if (!this.relatorioId || !this.relatorio) return;
    this.relatorioService.baixarPdf(this.relatorioId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.relatorio.numero_relatorio}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    });
  }

  // ── Assinatura ────────────────────────────────────────────
  podeAssinarComoEstagiario(): boolean {
    return this.relatorio?.status === 'Rascunho'
        && this.perfil === 'Estagiario'
        && !this.relatorio?.assinatura_estagiario;
  }

  podeAssinarComoDocente(): boolean {
    return this.relatorio?.status === 'Aguardando Assinatura do Docente'
        && (this.perfil === 'Docente' || this.perfil === 'Administrador')
        && !this.relatorio?.assinatura_docente;
  }

  abrirModalAssinatura() {
    this.modalAssinaturaAberto = true;
    this.senhaAssinatura = '';
  }

  fecharModalAssinatura() {
    this.modalAssinaturaAberto = false;
    this.senhaAssinatura = '';
  }

  confirmarAssinatura() {
    if (!this.senhaAssinatura.trim() || !this.relatorioId) return;
    this.isAssinando = true;
    this.errorMessage = '';
    this.relatorioService.assinar(this.relatorioId, this.senhaAssinatura).subscribe({
      next: (rel) => {
        this.relatorio = rel;
        this.isAssinando = false;
        this.fecharModalAssinatura();
        this.successMessage = rel.status === 'Finalizado'
          ? 'Relatório assinado e finalizado com sucesso!'
          : 'Sua assinatura foi registrada. Aguardando assinatura do preceptor.';
        this.carregarPreviewPdf();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isAssinando = false;
        this.errorMessage = err.error?.detail || 'Erro ao assinar relatório.';
        this.cdr.detectChanges();
      }
    });
  }

  voltar() {
    this.router.navigate(['/relatorios']);
  }

  isReadonly(): boolean {
    return this.modo === 'visualizar' && this.relatorio?.status !== 'Rascunho';
  }

  getStatusClass(s: string): string {
    return ({
      'Rascunho':                          'bg-gray-100 text-gray-700 border-gray-200',
      'Aguardando Assinatura do Docente':  'bg-amber-100 text-amber-700 border-amber-200',
      'Finalizado':                        'bg-green-100 text-green-700 border-green-200',
      'Cancelado':                         'bg-red-100 text-red-700 border-red-200'
    } as any)[s] || 'bg-gray-100 text-gray-700';
  }

  calcularIdade(data: string): number {
    if (!data) return 0;
    const nasc = new Date(data);
    const hoje = new Date();
    let idade = hoje.getFullYear() - nasc.getFullYear();
    const m = hoje.getMonth() - nasc.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
    return idade;
  }
}
