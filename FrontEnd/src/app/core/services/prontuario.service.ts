import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ProntuarioService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/prontuarios`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  criarTriagem(dados: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, dados, { headers: this.getHeaders() });
  }

  listarMeusProntuarios(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/meus`, { headers: this.getHeaders() });
  }

  buscarPorId(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  buscarPorPaciente(pacienteId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/paciente/${pacienteId}`, { headers: this.getHeaders() });
  }

}