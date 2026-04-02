import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login';
import { LayoutComponent } from './shared/layout/layout';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  
  // Rotas Protegidas (envolvidas pelo Layout)
  { 
    path: '', 
    component: LayoutComponent, 
    children: [
      { 
        path: 'dashboard', 
        loadComponent: () => import('./features/dashboard/painel-inicial/painel-inicial').then(m => m.PainelInicialComponent) 
      },
      { 
        path: 'usuarios', 
        loadComponent: () => import('./features/admin/gestao-usuarios/gestao-usuarios').then(m => m.GestaoUsuariosComponent) 
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  
  { path: '**', redirectTo: '/login' } // Qualquer rota não encontrada vai para o login
];