import { Component, inject, OnInit, OnDestroy, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../core/services/admin.service';

@Component({
  selector: 'app-monitoramento',
  standalone: true,
  imports: [CommonModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './monitoramento.html',
})
export class MonitoramentoComponent implements OnInit, OnDestroy {
  private adminService = inject(AdminService);
  private cdr          = inject(ChangeDetectorRef);

  dados: any   = null;
  isLoading    = true;
  erro         = '';
  ultimaAtualizacao: Date | null = null;
  autoRefresh  = true;
  private timer: any = null;

  ngOnInit() {
    this.carregar();
    if (this.autoRefresh) this.iniciarTimer();
  }

  ngOnDestroy() { this.pararTimer(); }

  carregar() {
    this.adminService.getMonitoramento().subscribe({
      next: (d) => {
        this.dados = d;
        this.ultimaAtualizacao = new Date();
        this.isLoading = false;
        this.erro = '';
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.erro = err?.error?.detail || 'Erro ao carregar monitoramento.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  toggleAutoRefresh() {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) this.iniciarTimer();
    else this.pararTimer();
  }

  private iniciarTimer() {
    this.pararTimer();
    this.timer = setInterval(() => this.carregar(), 10000);
  }

  private pararTimer() {
    if (this.timer) { clearInterval(this.timer); this.timer = null; }
  }

  // Helpers de formatação
  fmtBytes(bytes: number): string {
    if (!bytes && bytes !== 0) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
    return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
  }

  fmtNumber(n: number): string {
    if (n == null) return '—';
    return n.toLocaleString('pt-BR');
  }

  statusColor(status: string): string {
    if (status === '2xx') return 'bg-green-500';
    if (status === '3xx') return 'bg-blue-500';
    if (status === '4xx') return 'bg-amber-500';
    if (status === '5xx') return 'bg-red-500';
    return 'bg-gray-400';
  }

  pctBar(parte: number, total: number): number {
    if (!total) return 0;
    return Math.min(100, Math.round((parte / total) * 100));
  }

  totalStatus(): number {
    if (!this.dados?.trafego?.por_status) return 0;
    const v = this.dados.trafego.por_status;
    return (v['2xx'] || 0) + (v['3xx'] || 0) + (v['4xx'] || 0) + (v['5xx'] || 0);
  }

  perfisChaves(): string[] {
    if (!this.dados?.negocio?.usuarios_por_perfil) return [];
    return Object.keys(this.dados.negocio.usuarios_por_perfil);
  }

  metodosChaves(): string[] {
    if (!this.dados?.trafego?.por_metodo) return [];
    return Object.keys(this.dados.trafego.por_metodo);
  }

  perfilLabel(p: string): string {
    return p === 'Docente' ? 'Preceptor' : p;
  }

  perfilCor(p: string): string {
    if (p === 'Administrador') return 'bg-orange-100 text-orange-700';
    if (p === 'Docente')       return 'bg-blue-100 text-blue-700';
    if (p === 'Estagiario')    return 'bg-emerald-100 text-emerald-700';
    return 'bg-gray-100 text-gray-700';
  }

  statusBadge(status: number): string {
    if (status >= 500) return 'bg-red-100 text-red-700';
    if (status >= 400) return 'bg-amber-100 text-amber-700';
    if (status >= 300) return 'bg-blue-100 text-blue-700';
    if (status >= 200) return 'bg-green-100 text-green-700';
    return 'bg-gray-100 text-gray-700';
  }
}
