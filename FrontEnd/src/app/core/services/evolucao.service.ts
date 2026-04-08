import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class EvolucaoService {
  private http        = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl      = `${environment.apiUrl}/evolucoes`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  listarPorProntuario(prontuarioId: string): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/prontuario/${prontuarioId}`,
      { headers: this.getHeaders() }
    );
  }

  registrar(dados: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, dados, { headers: this.getHeaders() });
  }

  contarPendentesPorDocente(): Observable<{ count: number }> {
    return this.http.get<{ count: number }>(
      `${this.apiUrl}/pendentes/count`,
      { headers: this.getHeaders() }
    );
  }
}