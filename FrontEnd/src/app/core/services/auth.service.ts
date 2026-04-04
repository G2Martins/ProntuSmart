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
    const body = new URLSearchParams();
    body.set('username', matricula);
    body.set('password', senha);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<any>(`${this.apiUrl}/auth/login`, body.toString(), { headers }).pipe(
      tap(response => {
        if (response.access_token) {
          localStorage.setItem('prontusmart_token', response.access_token);
        }
      })
    );
  }

  getToken() {
    return localStorage.getItem('prontusmart_token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  logout() {
    localStorage.removeItem('prontusmart_token');
  }

  getUserProfile(): string | null {
    const token = this.getToken();
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.perfil || null;
    } catch (e) {
      return null;
    }
  }

  // --- NOVAS FUNÇÕES PARA TROCA DE SENHA ---
  // Lê o JWT e verifica se a flag de troca obrigatória é verdadeira
  needsPasswordChange(): boolean {
    const token = this.getToken();
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.precisa_trocar_senha === true;
    } catch (e) {
      return false;
    }
  }

  // Envia a senha atual/temporária e a nova para o BackEnd
  efetivarTrocaSenha(senha_temporaria: string, nova_senha: string) {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${this.getToken()}`);
    return this.http.post<any>(
      `${this.apiUrl}/auth/trocar-senha`, 
      { senha_temporaria, nova_senha }, 
      { headers }
    );
  }
}