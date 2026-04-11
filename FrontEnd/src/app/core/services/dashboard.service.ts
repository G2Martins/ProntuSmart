import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private http        = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl      = `${environment.apiUrl}/dashboard`;

  private getHeaders() {
    return new HttpHeaders().set('Authorization', `Bearer ${this.authService.getToken()}`);
  }

  getEpidemiologia(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/epidemiologia`, { headers: this.getHeaders() });
  }

  getProdutividade(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/produtividade`, { headers: this.getHeaders() });
  }

  getRiscos(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/riscos`, { headers: this.getHeaders() });
  }
}
