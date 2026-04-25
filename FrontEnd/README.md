<div align="center">

# ProntuSMART — Frontend

### Interface Web do Sistema de Prontuário Eletrônico da Clínica Escola de Fisioterapia — UCB

<br>

<p>
  <img src="https://img.shields.io/badge/Angular-21+-DD0031?style=for-the-badge&logo=angular&logoColor=white" alt="Angular">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/TypeScript-5+-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Tailwind_CSS-4+-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind">
  <br><br>
  <img src="https://img.shields.io/badge/Iconify-Phosphor_Icons-1C78C0?style=for-the-badge&logo=iconify&logoColor=white" alt="Iconify">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/RxJS-Reactive_Forms-B7178C?style=for-the-badge&logo=reactivex&logoColor=white" alt="RxJS">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Tema-Claro_Escuro-374151?style=for-the-badge&logo=darkreader&logoColor=white" alt="Tema">
</p>

</div>

---

## Sobre

SPA (Single Page Application) construída em Angular com componentes standalone e Tailwind CSS. Consome a API REST do backend ProntuSMART e oferece interfaces adaptadas por perfil — **Estagiário, Preceptor e Administrador** — com dashboard personalizado, gestão de prontuários, registro de testes funcionais (Avaliação Funcional, Sunny, Mini-BESTest), emissão de relatórios com assinatura digital, fluxo de cadastro público com aprovação e painel de monitoramento do sistema.

---

## Stack Tecnológico

| Componente | Tecnologia | Versão |
|:---|:---|:---|
| Framework | Angular | 21+ |
| Linguagem | TypeScript | 5+ |
| Estilização | Tailwind CSS | 4+ |
| Ícones | Iconify (Phosphor Icons) | — |
| Formulários | Angular Reactive Forms + Template Forms | — |
| HTTP Client | Angular HttpClient + Interceptor | — |
| Roteamento | Angular Router (lazy loading) | — |
| Tema | Serviço próprio (claro / escuro persistente) | — |

---

## Instalação e Execução

### 1. Pré-requisitos
- Node.js 20+ e npm instalados
- Angular CLI: `npm install -g @angular/cli`

### 2. Instalar Dependências
```bash
cd FrontEnd
npm install
```

### 3. Iniciar em Desenvolvimento
```bash
ng serve
```
Aplicação disponível em **`http://localhost:4200`**

O servidor recarrega automaticamente ao salvar qualquer arquivo fonte.

### 4. Build de Produção
```bash
ng build
```
Artefatos gerados na pasta `dist/` com otimizações de performance (lazy chunks por feature).

---

## Arquitetura de Pastas

```
src/
│
├── index.html                              # Ponto de entrada HTML
├── main.ts                                 # Bootstrap Angular
├── styles.scss                             # Estilos globais e diretivas Tailwind
│
├── environments/
│   ├── environment.ts                      # Produção (URL da API)
│   └── environment.development.ts          # Desenvolvimento (URL local)
│
└── app/
    │
    ├── app.ts / app.html / app.config.ts   # Componente raiz e providers
    ├── app.routes.ts                       # Rotas com lazy loading por feature
    │
    ├── core/                               # Infraestrutura (sem UI)
    │   ├── guards/auth-guard.ts            # Protege rotas autenticadas
    │   ├── interceptors/auth.interceptor.ts # Injeta Authorization: Bearer
    │   └── services/                       # Clientes HTTP da API
    │       ├── auth.service.ts             # Login, logout, JWT decode, /auth/me
    │       ├── admin.service.ts            # Usuários, solicitações, monitoramento
    │       ├── area.service.ts
    │       ├── cid.service.ts
    │       ├── dashboard.service.ts
    │       ├── evolucao.service.ts
    │       ├── indicador.service.ts
    │       ├── meta-smart.service.ts
    │       ├── paciente.service.ts
    │       ├── prontuario.service.ts
    │       ├── relatorio.service.ts        # Relatórios + assinatura + PDF
    │       ├── teste.service.ts            # Testes/escalas aplicadas
    │       └── theme.service.ts            # Modo claro/escuro persistente
    │
    ├── features/                           # Módulos lazy loaded
    │   │
    │   ├── auth/
    │   │   ├── login/                      # Tabs Entrar / Registrar-se (cadastro público)
    │   │   └── trocar-senha/               # Troca obrigatória no primeiro acesso
    │   │
    │   ├── dashboard/
    │   │   ├── painel-inicial/             # Painel por perfil + caixa de solicitações (Admin)
    │   │   └── inteligencia-epidemiologica/
    │   │
    │   ├── pacientes/
    │   │   ├── busca-pacientes/
    │   │   └── cadastro-paciente/          # Triagem integrada (Estagiário)
    │   │
    │   ├── prontuarios/
    │   │   ├── visao-prontuario/           # Abas: Evoluções · Metas · Gráficos · Testes · Ficha Detalhada
    │   │   ├── insercao-evolucao/
    │   │   ├── avaliacao-funcional/        # Wizard de 3 partes (Mobilidade / AVDs / Síntese)
    │   │   ├── insercao-meta-smart/
    │   │   ├── revisao-evolucoes/          # Caixa de revisão do Preceptor
    │   │   ├── teste-sunny/                # Escala de Sunny (16 itens · 0-3)
    │   │   └── teste-mini-best/            # Mini-BESTest (14 itens · 0-2 · cutoff de queda)
    │   │
    │   ├── relatorios/
    │   │   ├── lista-relatorios/           # Caixas separadas por perfil + histórico
    │   │   └── gerar-relatorio/            # Editor + preview de PDF + assinatura digital
    │   │
    │   ├── admin/
    │   │   ├── gestao-usuarios/
    │   │   ├── gestao-areas/
    │   │   ├── gestao-cids/
    │   │   ├── gestao-indicadores/
    │   │   └── monitoramento/              # Métricas de runtime + DB + tráfego em tempo real
    │   │
    │   └── perfil/
    │       └── meu-perfil/                 # Dados, atividade, troca de senha
    │
    └── shared/
        ├── layout/                         # Sidebar (com aba Monitoramento), header, footer, tema
        ├── models/
        │   └── indicador.model.ts
        └── utils/
            └── indicador-limites.ts        # Helpers de validação de limites
```

---

## Roteamento

Todas as rotas de feature são **lazy loaded** para otimizar o bundle inicial. O guard `authGuard` protege as rotas internas redirecionando para `/login` quando não há token válido.

| Rota | Componente | Acesso |
|:---|:---|:---|
| `/login` | LoginComponent (com aba Registrar-se) | Público |
| `/trocar-senha` | TrocarSenhaComponent | Público |
| `/dashboard` | PainelInicialComponent | Autenticado |
| `/dashboard/epidemiologia` | InteligenciaEpidemiologicaComponent | Autenticado |
| `/pacientes` | BuscaPacientesComponent | Autenticado |
| `/pacientes/novo` · `/pacientes/editar/:id` | CadastroPacienteComponent | Autenticado |
| `/prontuarios/visao/:id` | VisaoProntuario | Autenticado |
| `/prontuarios/evoluir/:id` | InsercaoEvolucaoComponent | Estagiário |
| `/prontuarios/avaliacao/:id` | AvaliacaoFuncionalComponent | Estagiário |
| `/prontuarios/meta/:id` | InsercaoMetaSmartComponent | Estagiário |
| `/prontuarios/revisao` | RevisaoEvolucoesComponent | Preceptor |
| `/prontuarios/teste-sunny/:prontuarioId` | TesteSunnyComponent | Estagiário |
| `/prontuarios/teste-sunny/visualizar/:id` | TesteSunnyComponent | Autenticado |
| `/prontuarios/teste-mini-best/:prontuarioId` | TesteMiniBestComponent | Estagiário |
| `/prontuarios/teste-mini-best/visualizar/:id` | TesteMiniBestComponent | Autenticado |
| `/relatorios` | ListaRelatoriosComponent | Autenticado |
| `/relatorios/novo/:prontuarioId` · `/relatorios/visualizar/:id` | GerarRelatorioComponent | Autenticado |
| `/usuarios` | GestaoUsuariosComponent | Administrador |
| `/indicadores` | GestaoIndicadoresComponent | Administrador |
| `/areas` | GestaoAreasComponent | Administrador |
| `/cids` | GestaoCidsComponent | Administrador |
| `/monitoramento` | MonitoramentoComponent | Administrador |
| `/meu-perfil` | MeuPerfilComponent | Autenticado |

---

## Visões por Perfil

| Perfil | Visões principais |
|:---|:---|
| **Estagiário** | Painel com fila de avaliação · Triagem (cadastro de paciente + prontuário) · Avaliação Funcional · Metas SMART · Evoluções · Testes · Caixa de relatórios próprios para assinar |
| **Preceptor** | Painel com pendências · Caixa de revisão de evoluções · Caixa de relatórios aguardando assinatura sua · Inteligência Epidemiológica |
| **Administrador** | KPIs do sistema · Caixa de solicitações de cadastro · Gestão de Usuários / Áreas / CIDs / Indicadores · **Monitoramento** detalhado |

> A clínica chama o supervisor docente de **Preceptor**. O enum interno do JWT segue `Docente` por compatibilidade com o backend, mas toda a UI exibe **Preceptor**.

---

## Autenticação no Frontend

O `AuthService` decodifica o payload JWT localmente para leitura rápida de perfil, nome e ID:

```typescript
getUserProfile(): string  // 'Estagiario' | 'Docente' | 'Administrador'
getUserName(): string     // Nome completo extraído do token
getUserId(): string       // ObjectId do usuário (campo 'sub' do JWT)
needsPasswordChange(): boolean
getMe(): Observable<any>  // GET /auth/me
```

O `AuthInterceptor` adiciona automaticamente o header `Authorization: Bearer <token>` em toda requisição HTTP autenticada.

A tela de login traz a aba **Registrar-se**, que envia uma solicitação pública via `POST /auth/registrar`. O acesso só é liberado após aprovação do Administrador na caixa de solicitações do painel.

---

## Convenções de Desenvolvimento

- **Componentes standalone**: todos com `standalone: true` — sem NgModules.
- **CUSTOM_ELEMENTS_SCHEMA**: necessário em componentes que usam tags `<iconify-icon>`.
- **ChangeDetectorRef**: usado manualmente em callbacks de `subscribe()` para forçar render quando necessário.
- **Reactive Forms** para formulários complexos; `FormsModule` apenas em campos pontuais (busca / observações).
- **Lazy Loading**: todas as features via `loadComponent()` no `app.routes.ts`.
- **Tailwind**: estilização exclusivamente por classes utilitárias; suporte a tema claro/escuro via classes `dark:`.
- **Hints de depreciação `*ngIf` / `*ngFor`**: o codebase mantém o padrão atual; migração para control flow nativo (`@if` / `@for`) fica para refactor futuro.

---

<div align="center">
  <br>
  &copy; 2026 Clínica Escola de Fisioterapia — UCB. Todos os direitos reservados.
  <br><br>
  Desenvolvido por <strong>Gustavo Martins Gripaldi</strong> e <strong>João Victor Rodrigues Pinto</strong>
</div>
