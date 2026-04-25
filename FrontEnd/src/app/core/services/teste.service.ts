import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

export type TipoTeste = 'AvaliacaoFuncional' | 'Sunny' | 'MiniBest';

export interface Teste {
  _id?: string;
  prontuario_id: string;
  paciente_id?: string;
  aplicador_id?: string;
  nome_aplicador?: string;
  tipo: TipoTeste;
  dados: any;
  pontuacao_total?: number;
  pontuacao_maxima?: number;
  interpretacao?: string;
  observacoes?: string;
  data_aplicacao?: string;
  criado_em?: string;
}

@Injectable({ providedIn: 'root' })
export class TesteService {
  private http        = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl      = `${environment.apiUrl}/testes`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  criar(payload: Partial<Teste>): Observable<Teste> {
    return this.http.post<Teste>(`${this.apiUrl}/`, payload, { headers: this.getHeaders() });
  }

  listarPorProntuario(prontuarioId: string, tipo?: TipoTeste): Observable<Teste[]> {
    const qs = tipo ? `?tipo=${tipo}` : '';
    return this.http.get<Teste[]>(
      `${this.apiUrl}/prontuario/${prontuarioId}${qs}`,
      { headers: this.getHeaders() }
    );
  }

  buscarPorId(id: string): Observable<Teste> {
    return this.http.get<Teste>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  atualizar(id: string, payload: any): Observable<Teste> {
    return this.http.patch<Teste>(`${this.apiUrl}/${id}`, payload, { headers: this.getHeaders() });
  }

  excluir(id: string) {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}
