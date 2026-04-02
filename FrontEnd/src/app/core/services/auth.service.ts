import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  login(matricula: string, senha: string) {
    // O FastAPI com OAuth2 espera receber os dados em URL Encoded, com os campos exatos 'username' e 'password'
    const body = new URLSearchParams();
    body.set('username', matricula);
    body.set('password', senha);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<any>(`${this.apiUrl}/auth/login`, body.toString(), { headers }).pipe(
      tap(response => {
        // Se a API retornar o token, nós o salvamos no navegador
        if (response.access_token) {
          localStorage.setItem('prontusmart_token', response.access_token);
        }
      })
    );
  }

  // Funções utilitárias para usarmos no futuro (ex: para proteger rotas)
  getToken() {
    return localStorage.getItem('prontusmart_token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  logout() {
    localStorage.removeItem('prontusmart_token');
  }
}