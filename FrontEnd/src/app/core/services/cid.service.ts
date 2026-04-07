import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class CidService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/cids`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  listar() { return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders() }); }
  
  buscar(termo: string = '', limit: number = 50) {
  const params = new HttpParams()
    .set('busca', termo)
    .set('limit', limit.toString());
  return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders(), params });
}
  criar(dados: any) { return this.http.post<any>(this.apiUrl, dados, { headers: this.getHeaders() }); }
  
  atualizar(id: string, dados: any) { return this.http.put<any>(`${this.apiUrl}/${id}`, dados, { headers: this.getHeaders() }); }
  
  importarLote(dados: any[]) { 
    return this.http.post<any>(`${this.apiUrl}/bulk`, dados, { headers: this.getHeaders() }); 
  }
}