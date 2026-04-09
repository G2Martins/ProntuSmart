import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login';
import { LayoutComponent } from './shared/layout/layout';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: 'trocar-senha', 
    loadComponent: () => import('./features/auth/trocar-senha/trocar-senha').then(m => m.TrocarSenhaComponent)
  },
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
      { 
        path: 'areas', 
        loadComponent: () => import('./features/admin/gestao-areas/gestao-areas').then(m => m.GestaoAreasComponent) 
      },
      { 
        path: 'cids', 
        loadComponent: () => import('./features/admin/gestao-cids/gestao-cids').then(m => m.GestaoCidsComponent) 
      },
      { 
        path: 'pacientes', 
        loadComponent: () => import('./features/pacientes/busca-pacientes/busca-pacientes').then(m => m.BuscaPacientesComponent) 
      },
      { 
        path: 'pacientes/novo', 
        loadComponent: () => import('./features/pacientes/cadastro-paciente/cadastro-paciente').then(m => m.CadastroPacienteComponent) 
      },
      { 
        path: 'pacientes/editar/:id', 
        loadComponent: () => import('./features/pacientes/cadastro-paciente/cadastro-paciente').then(m => m.CadastroPacienteComponent) 
      },
      {
        path: 'prontuarios/visao/:id',
        loadComponent: () => import('./features/prontuarios/visao-prontuario/visao-prontuario').then(m => m.VisaoProntuario)
      },
      {
        path: 'prontuarios/evoluir/:id',
        loadComponent: () => import('./features/prontuarios/insercao-evolucao/insercao-evolucao').then(m => m.InsercaoEvolucaoComponent)
      },
      {
        path: 'prontuarios/avaliacao/:id',
        loadComponent: () => import('./features/prontuarios/avaliacao-funcional/avaliacao-funcional').then(m => m.AvaliacaoFuncionalComponent)
      },  
      {
        path: 'prontuarios/meta/:id',
        loadComponent: () => import('./features/prontuarios/insercao-meta-smart/insercao-meta-smart').then(m => m.InsercaoMetaSmartComponent)
      },
      {
        path: 'prontuarios/revisao',
        loadComponent: () => import('./features/prontuarios/revisao-evolucoes/revisao-evolucoes').then(m => m.RevisaoEvolucoesComponent), canActivate: [authGuard]
      },
      {
        path: 'dashboard/epidemiologia',
        loadComponent: () => import('./features/dashboard/inteligencia-epidemiologica/inteligencia-epidemiologica').then(m => m.InteligenciaEpidemiologicaComponent)
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  
  { path: '**', redirectTo: '/login' } 
];