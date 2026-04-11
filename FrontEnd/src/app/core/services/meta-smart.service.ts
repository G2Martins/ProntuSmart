import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class MetaSmartService {
  private http        = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl      = `${environment.apiUrl}/metas-smart`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  listarPorProntuario(prontuarioId: string): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/prontuario/${prontuarioId}`,
      { headers: this.getHeaders() }
    );
  }

  criar(dados: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, dados, { headers: this.getHeaders() });
  }

  editar(metaId: string, dados: any): Observable<any> {
    return this.http.patch<any>(
      `${this.apiUrl}/${metaId}`,
      dados,
      { headers: this.getHeaders() }
    );
  }

  cancelar(metaId: string, status: string, motivo: string): Observable<any> {
    return this.http.patch<any>(
      `${this.apiUrl}/${metaId}/status`,
      { status, motivo },
      { headers: this.getHeaders() }
    );
  }
}