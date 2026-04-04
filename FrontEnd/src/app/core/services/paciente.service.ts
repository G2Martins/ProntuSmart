import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class PacienteService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/pacientes`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  listar() { return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders() }); }
  buscarPorId(id: string) { return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() }); }
  criar(dados: any) { return this.http.post<any>(this.apiUrl, dados, { headers: this.getHeaders() }); }
  atualizar(id: string, dados: any) { return this.http.patch<any>(`${this.apiUrl}/${id}`, dados, { headers: this.getHeaders() }); }
}