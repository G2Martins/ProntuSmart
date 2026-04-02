import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login'; // Certifique-se que o caminho está correto

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' }, // Redireciona a raiz para o login
  { path: '**', redirectTo: '/login' } // Qualquer rota não encontrada vai para o login (por enquanto)
];