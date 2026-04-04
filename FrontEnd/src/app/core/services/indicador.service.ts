import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';
import { Indicador, IndicadorCreate, IndicadorUpdate } from '../../shared/models/indicador.model';

@Injectable({ providedIn: 'root' })
export class IndicadorService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/indicadores`;

  private getHeaders() {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  listar(apenasAtivos = false): Observable<Indicador[]> {
    return this.http.get<Indicador[]>(
      `${this.apiUrl}/?apenas_ativos=${apenasAtivos}`,
      { headers: this.getHeaders() }
    );
  }

  criar(dados: IndicadorCreate): Observable<Indicador> {
    return this.http.post<Indicador>(this.apiUrl + '/', dados, { headers: this.getHeaders() });
  }

  atualizar(id: string, dados: IndicadorUpdate): Observable<Indicador> {
    return this.http.put<Indicador>(`${this.apiUrl}/${id}`, dados, { headers: this.getHeaders() });
  }

  toggleStatus(id: string, isAtivo: boolean): Observable<Indicador> {
    return this.http.put<Indicador>(
      `${this.apiUrl}/${id}`,
      { is_ativo: isAtivo },
      { headers: this.getHeaders() }
    );
  }

  deletar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}