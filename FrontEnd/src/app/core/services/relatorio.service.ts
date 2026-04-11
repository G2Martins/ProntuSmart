import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class RelatorioService {
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/relatorios`;

  private headers() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.auth.getToken()}`);
  }

  criar(dados: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, dados, { headers: this.headers() });
  }

  listarMeus(filtros?: { tipo?: string; status?: string }): Observable<any[]> {
    let url = `${this.apiUrl}/meus`;
    const qs: string[] = [];
    if (filtros?.tipo)   qs.push(`tipo=${encodeURIComponent(filtros.tipo)}`);
    if (filtros?.status) qs.push(`status=${encodeURIComponent(filtros.status)}`);
    if (qs.length) url += `?${qs.join('&')}`;
    return this.http.get<any[]>(url, { headers: this.headers() });
  }

  buscarPorId(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.headers() });
  }

  atualizar(id: string, dados: any): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/${id}`, dados, { headers: this.headers() });
  }

  assinar(id: string, senha: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/assinar`, { senha }, { headers: this.headers() });
  }

  cancelar(id: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.headers() });
  }

  /** Retorna o blob do PDF para download/preview inline. */
  baixarPdf(id: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/${id}/pdf`, {
      headers: this.headers(),
      responseType: 'blob'
    });
  }
}
