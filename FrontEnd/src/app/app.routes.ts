import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login';
import { LayoutComponent } from './shared/layout/layout';
import { authGuard } from './core/guards/auth-guard'; 

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  
  { 
    path: '', 
    component: LayoutComponent, 
    canActivate: [authGuard], 
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
  
  { path: '**', redirectTo: '/login' } 
];