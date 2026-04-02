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

  // NOVA FUNÇÃO: Descodifica o JWT para descobrir o perfil logado
  getUserProfile(): string | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      // O JWT tem 3 partes separadas por ponto. A segunda parte é o Payload (dados).
      const payloadBase64 = token.split('.')[1];
      const payloadDecoded = JSON.parse(atob(payloadBase64));
      return payloadDecoded.perfil || null;
    } catch (e) {
      console.error('Erro ao descodificar o token', e);
      return null;
    }
  }
}