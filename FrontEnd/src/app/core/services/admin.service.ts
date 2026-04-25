import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';
import { Observable } from 'rxjs/internal/Observable';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/admin`;

  // Função utilitária para injetar o Token em todas as requisições deste serviço
  private getHeaders() {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Vai buscar as estatísticas reais ao MongoDB
  getEstatisticas() {
    return this.http.get<any>(`${this.apiUrl}/estatisticas`, { headers: this.getHeaders() });
  }

  getMonitoramento() {
    return this.http.get<any>(`${this.apiUrl}/monitoramento`, { headers: this.getHeaders() });
  }

  getUsuarios(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios`, { headers: this.getHeaders() });
  }

  // Prepara o terreno para criarmos o Estagiário na próxima etapa!
  criarUsuario(usuarioData: any) {
    return this.http.post<any>(`${this.apiUrl}/usuarios`, usuarioData, { headers: this.getHeaders() });
  }
  
  listarUsuarios(perfil?: string, ativo?: boolean) {
    let params = '';
    if (perfil || ativo !== undefined) {
      params = `?${perfil ? 'perfil=' + perfil : ''}${ativo !== undefined ? '&is_ativo=' + ativo : ''}`;
    }
    return this.http.get<any[]>(`${this.apiUrl}/usuarios${params}`, { headers: this.getHeaders() });
  }

  listarEstagiarios(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/estagiarios`, { headers: this.getHeaders() });
  }

  atualizarUsuario(id: string, dados: any) {
    return this.http.put<any>(`${this.apiUrl}/usuarios/${id}`, dados, { headers: this.getHeaders() });
  }

  resetarSenha(id: string) {
    return this.http.patch<{nova_senha: string}>(`${this.apiUrl}/usuarios/${id}/reset-password`, {}, { headers: this.getHeaders() });
  }

  // ── Solicitações de cadastro ─────────────────────────────
  listarSolicitacoes(status?: string): Observable<any[]> {
    const qs = status ? `?status=${encodeURIComponent(status)}` : '';
    return this.http.get<any[]>(`${this.apiUrl}/solicitacoes${qs}`, { headers: this.getHeaders() });
  }

  contarSolicitacoesPendentes(): Observable<{ pendentes: number }> {
    return this.http.get<{ pendentes: number }>(
      `${this.apiUrl}/solicitacoes/contagem`, { headers: this.getHeaders() }
    );
  }

  aprovarSolicitacao(id: string, edits: any) {
    return this.http.patch<any>(
      `${this.apiUrl}/solicitacoes/${id}/aprovar`, edits, { headers: this.getHeaders() }
    );
  }

  recusarSolicitacao(id: string, motivo_recusa: string) {
    return this.http.patch<any>(
      `${this.apiUrl}/solicitacoes/${id}/recusar`, { motivo_recusa }, { headers: this.getHeaders() }
    );
  }
}