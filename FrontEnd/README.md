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
  <img src="https://img.shields.io/badge/Tests-Vitest-6E9F18?style=for-the-badge&logo=vitest&logoColor=white" alt="Vitest">
</p>

</div>

---

## Sobre

SPA (Single Page Application) construída em Angular com componentes standalone e Tailwind CSS. Consome a API REST do backend ProntuSMART e oferece interfaces adaptadas por perfil: Estagiário, Docente e Administrador — com dashboard personalizado, gestão de prontuários e recursos de análise clínica.

---

## Stack Tecnológico

| Componente | Tecnologia | Versão |
|:---|:---|:---|
| Framework | Angular | 21+ |
| Linguagem | TypeScript | 5+ |
| Estilização | Tailwind CSS | 4+ |
| Ícones | Iconify (Phosphor Icons) | — |
| Formulários | Angular Reactive Forms | — |
| HTTP Client | Angular HttpClient + Interceptor | — |
| Roteamento | Angular Router (lazy loading) | — |
| Testes | Vitest | — |

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
Artefatos gerados na pasta `dist/` com otimizações de performance aplicadas.

### 5. Executar Testes
```bash
ng test
```
Testes unitários com Vitest.

---

## Arquitetura de Pastas

```
src/
│
├── index.html                              # Ponto de entrada HTML da aplicação
├── main.ts                                 # Bootstrap Angular: registra providers e inicia o app
├── styles.scss                             # Estilos globais e diretivas Tailwind (@tailwind base, etc.)
│
├── environments/
│   ├── environment.ts                      # Configuração de produção (URL da API, flags de feature)
│   └── environment.development.ts          # Configuração de desenvolvimento (URL local do backend)
│
└── app/
    │
    ├── app.ts                              # Componente raiz da aplicação
    ├── app.html                            # Template raiz (contém <router-outlet>)
    ├── app.routes.ts                       # Definição de todas as rotas com lazy loading por feature
    ├── app.config.ts                       # Providers globais: HttpClient, Router, Interceptors
    │
    ├── core/                               # Infraestrutura central — não contém UI
    │   │
    │   ├── guards/
    │   │   └── auth-guard.ts               # Protege rotas: redireciona para /login se não autenticado
    │   │
    │   ├── interceptors/
    │   │   └── auth.interceptor.ts         # Injeta o header Authorization: Bearer <token> em todas as requisições
    │   │
    │   └── services/                       # Serviços HTTP que consomem a API do backend
    │       ├── auth.service.ts             # Login, logout, decodificação JWT, getUserProfile/Name/Id, getMe()
    │       ├── admin.service.ts            # Gestão de usuários e estatísticas administrativas
    │       ├── area.service.ts             # CRUD de áreas clínicas
    │       ├── cid.service.ts              # Busca e gestão de códigos CID-10
    │       ├── dashboard.service.ts        # Dados para dashboards e inteligência epidemiológica
    │       ├── evolucao.service.ts         # Registro de evoluções e contagem de pendentes por docente
    │       ├── indicador.service.ts        # CRUD de indicadores clínicos
    │       ├── meta-smart.service.ts       # Criação e listagem de metas SMART
    │       ├── paciente.service.ts         # Busca, cadastro e edição de pacientes
    │       └── prontuario.service.ts       # Abertura, listagem e visão completa de prontuários
    │
    ├── features/                           # Módulos funcionais da aplicação (lazy loaded)
    │   │
    │   ├── auth/
    │   │   ├── login/                      # Tela de login: formulário de matrícula e senha com JWT
    │   │   └── trocar-senha/               # Tela de troca de senha obrigatória no primeiro acesso
    │   │
    │   ├── dashboard/
    │   │   ├── painel-inicial/             # Dashboard principal: stats e ações contextuais por perfil
    │   │   └── inteligencia-epidemiologica/ # Gráficos de produtividade, distribuição de diagnósticos e alertas
    │   │
    │   ├── pacientes/
    │   │   ├── busca-pacientes/            # Listagem e busca de pacientes com filtros por nome e CPF
    │   │   └── cadastro-paciente/          # Formulário de cadastro e edição de paciente (rota /novo e /editar/:id)
    │   │
    │   ├── prontuarios/
    │   │   ├── visao-prontuario/           # Visão completa do prontuário: metas, evoluções, medições e gráficos
    │   │   ├── insercao-evolucao/          # Formulário de registro de sessão de atendimento
    │   │   ├── avaliacao-funcional/        # Formulário de avaliação funcional inicial do paciente
    │   │   ├── insercao-meta-smart/        # Formulário de criação de meta SMART com 5 componentes
    │   │   └── revisao-evolucoes/          # Fila de evoluções pendentes de revisão (perfil Docente)
    │   │
    │   ├── admin/
    │   │   ├── gestao-usuarios/            # Listagem, cadastro e ativação/desativação de usuários
    │   │   ├── gestao-areas/               # CRUD de áreas clínicas disponíveis na clínica
    │   │   ├── gestao-cids/                # CRUD de códigos diagnósticos CID-10
    │   │   └── gestao-indicadores/         # CRUD de indicadores clínicos com direção de melhora e unidade
    │   │
    │   └── perfil/
    │       └── meu-perfil/                 # Página de perfil do usuário: dados, estatísticas e troca de senha
    │
    └── shared/                             # Componentes e modelos reutilizáveis entre features
        ├── layout/                         # Layout principal: sidebar de navegação, header com avatar e footer
        └── models/
            └── indicador.model.ts          # Interface TypeScript para o modelo de indicador clínico
```

---

## Roteamento

Todas as rotas de feature são **lazy loaded** para otimizar o bundle inicial. O guard `authGuard` protege as rotas internas redirecionando para `/login` quando não há token válido.

| Rota | Componente | Acesso |
|:---|:---|:---|
| `/login` | LoginComponent | Público |
| `/trocar-senha` | TrocarSenhaComponent | Público |
| `/dashboard` | PainelInicialComponent | Autenticado |
| `/dashboard/epidemiologia` | InteligenciaEpidemiologicaComponent | Autenticado |
| `/pacientes` | BuscaPacientesComponent | Autenticado |
| `/pacientes/novo` | CadastroPacienteComponent | Autenticado |
| `/pacientes/editar/:id` | CadastroPacienteComponent | Autenticado |
| `/prontuarios/visao/:id` | VisaoProntuario | Autenticado |
| `/prontuarios/evoluir/:id` | InsercaoEvolucaoComponent | Autenticado |
| `/prontuarios/avaliacao/:id` | AvaliacaoFuncionalComponent | Autenticado |
| `/prontuarios/meta/:id` | InsercaoMetaSmartComponent | Autenticado |
| `/prontuarios/revisao` | RevisaoEvolucoesComponent | Autenticado |
| `/usuarios` | GestaoUsuariosComponent | Administrador |
| `/indicadores` | GestaoIndicadoresComponent | Administrador |
| `/areas` | GestaoAreasComponent | Administrador |
| `/cids` | GestaoCidsComponent | Administrador |
| `/meu-perfil` | MeuPerfilComponent | Autenticado |

---

## Autenticação no Frontend

O `AuthService` decodifica o payload JWT localmente (sem requisição ao servidor) para leitura rápida de perfil e nome:

```typescript
getUserProfile(): string  // 'Estagiario' | 'Docente' | 'Administrador'
getUserName(): string     // Nome completo extraído do token
getUserId(): string       // ObjectId do usuário (campo 'sub' do JWT)
getMe(): Observable<any>  // GET /auth/me — dados completos do usuário autenticado
```

O `AuthInterceptor` adiciona automaticamente o header `Authorization: Bearer <token>` em toda requisição HTTP que não seja para `/auth/login`.

---

## Convenções de Desenvolvimento

- **Componentes standalone**: todos os componentes usam `standalone: true` — sem NgModules.
- **CUSTOM_ELEMENTS_SCHEMA**: necessário nos componentes que usam tags `<iconify-icon>`.
- **ChangeDetectorRef**: usado manualmente em callbacks de `subscribe()` para atualizar a view.
- **Reactive Forms**: todos os formulários usam `FormBuilder` e `Validators` — sem template-driven forms.
- **Lazy Loading**: todas as features são importadas via `loadComponent()` no arquivo de rotas.
- **Tailwind CSS**: estilização exclusivamente por classes utilitárias — sem CSS customizado por componente.

---

<div align="center">
  <br>
  &copy; 2026 Clínica Escola de Fisioterapia — UCB. Todos os direitos reservados.
  <br><br>
  Desenvolvido por <strong>Gustavo Martins Gripaldi</strong> e <strong>João Victor Rodrigues Pinto</strong>
</div>
