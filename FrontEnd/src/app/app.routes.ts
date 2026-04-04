import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login';
import { LayoutComponent } from './shared/layout/layout';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  
  // NOVA ROTA (Fora do Layout, sem menu lateral)
  { 
    path: 'trocar-senha', 
    loadComponent: () => import('./features/auth/trocar-senha/trocar-senha').then(m => m.TrocarSenhaComponent)
  },
  
  // Rotas Protegidas (envolvidas pelo Layout e pelo Guardião)
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
      {
        path: 'indicadores',
        loadComponent: () => import('./features/admin/gestao-indicadores/gestao-indicadores')
          .then(m => m.GestaoIndicadoresComponent)
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  
  { path: '**', redirectTo: '/login' } 
];