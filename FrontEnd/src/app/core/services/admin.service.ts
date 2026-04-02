import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

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

  // Prepara o terreno para criarmos o Estagiário na próxima etapa!
  criarUsuario(usuarioData: any) {
    return this.http.post<any>(`${this.apiUrl}/usuarios`, usuarioData, { headers: this.getHeaders() });
  }
}