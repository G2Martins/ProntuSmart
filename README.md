<div align="center">

# ProntuSMART

### Sistema de Prontuário Eletrônico para Clínica Escola de Fisioterapia

<br>

<p>
  <img src="https://img.shields.io/badge/Frontend-Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white" alt="Angular">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Styling-Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind">
  <br><br>
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
</p>

<p>
  <strong>Clínica Escola de Fisioterapia — Universidade Católica de Brasília | 2025/2026</strong>
</p>

</div>

---

## Sobre o Projeto

O **ProntuSMART** é um sistema de prontuário eletrônico desenvolvido para a Clínica Escola de Fisioterapia da UCB. A plataforma digitaliza e centraliza o fluxo clínico entre administradores, docentes e estagiários, substituindo registros manuais por uma solução web segura, rastreável e orientada a dados.

O sistema implementa o método **SMART** para registro estruturado de metas clínicas, garantindo rastreabilidade dos tratamentos, supervisão acadêmica dos estagiários e geração de indicadores para a gestão da clínica.

### Objetivos
- Digitalizar o ciclo completo de atendimento fisioterapêutico na clínica escola.
- Implementar controle de acesso por perfil (RBAC) para Administradores, Docentes e Estagiários.
- Garantir imutabilidade e rastreabilidade legal dos dados clínicos.
- Fornecer indicadores de produtividade e inteligência epidemiológica.

---

## Arquitetura da Solução

O sistema é composto por duas aplicações independentes que se comunicam via API REST:

```
ProntuSmart/
├── BackEnd/     → API REST em Python/FastAPI com MongoDB
└── FrontEnd/    → SPA (Single Page Application) em Angular com Tailwind CSS
```

**Fluxo de funcionamento:**
1. O usuário acessa o frontend Angular via navegador.
2. A autenticação via matrícula e senha gera um token JWT com perfil embutido.
3. O interceptor HTTP injeta o token em todas as requisições subsequentes.
4. O backend valida o token, aplica as regras de negócio por perfil e persiste no MongoDB.

---

## Perfis de Usuário

| Perfil | Descrição |
|:---|:---|
| **Administrador** | Gestão de usuários, áreas clínicas, CIDs, indicadores; aprovação de solicitações de cadastro; painel de monitoramento profundo do sistema |
| **Preceptor** *(enum interno: Docente)* | Supervisão de estagiários, revisão e coassinatura de evoluções, assinatura de relatórios fisioterapêuticos |
| **Estagiário** | Triagem de pacientes, registro de evoluções, avaliações funcionais, metas SMART, aplicação de testes (Avaliação Funcional / Sunny / Mini-BESTest) e emissão de relatórios |

---

## Módulos do Projeto

### Backend — API REST (FastAPI + MongoDB)
Instruções de instalação, configuração e endpoints da API:
📄 [Documentação do Backend](./BackEnd/README.md)

### Frontend — Interface Web (Angular + Tailwind)
Instruções de instalação, execução e estrutura da aplicação:
📄 [Documentação do Frontend](./FrontEnd/README.md)

---

## Início Rápido

### Pré-requisitos
- Python 3.10+ e pip
- Node.js 20+ e npm
- Instância MongoDB (local ou Atlas)

### 1. Iniciar o Backend
```bash
cd BackEnd
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Configure .env com base no .env.example
python -m src.utils.seed         # Popula áreas + indicadores + 3 contas-base (sem pacientes)
uvicorn src.main:app --reload
```
API disponível em `http://localhost:8000` | Swagger em `http://localhost:8000/docs`

> A seed cria as contas: `admin01` (Administrador), `prec01` / **Velluma** (Preceptor — Neurologia Adulto) e `est01` / **Emellyn Lima** (Estagiária — Neurologia Adulto). Todas com senha `ucb@1234`.

### 2. Iniciar o Frontend
```bash
cd FrontEnd
npm install
ng serve
```
Aplicação disponível em `http://localhost:4200`

---

## Stack Tecnológica

| Camada | Tecnologia | Versão |
|:---|:---|:---|
| Framework Frontend | Angular | 21+ |
| Estilização | Tailwind CSS | 4+ |
| Ícones | Iconify (Phosphor Icons) | — |
| Framework Backend | FastAPI | 0.110.0 |
| Servidor ASGI | Uvicorn | 0.29.0 |
| Banco de Dados | MongoDB | 4.4+ |
| Driver Async BD | Motor | 3.6+ |
| Validação de Dados | Pydantic | 2.6.3+ |
| Autenticação | JWT (python-jose) | 3.3.0 |
| Criptografia de Senha | bcrypt | 4.1.2 |

---

## Funcionalidades

| Status | Funcionalidade |
|:---:|:---|
| ✅ | Autenticação JWT com controle de perfil (RBAC) |
| ✅ | Cadastro público com aprovação manual do Administrador |
| ✅ | Gestão completa de pacientes (CRUD) |
| ✅ | Triagem exclusiva pelo Estagiário (abertura de prontuário com CID) |
| ✅ | Prontuários eletrônicos com ciclo de vida controlado |
| ✅ | Registro de evoluções clínicas com revisão e coassinatura do Preceptor |
| ✅ | Avaliação funcional estruturada em wizard de 3 partes |
| ✅ | Histórico de testes/escalas: Avaliação Funcional, Escala de Sunny e Mini-BESTest |
| ✅ | Metas SMART com acompanhamento de progresso |
| ✅ | Medições e indicadores clínicos por meta |
| ✅ | Relatórios fisioterapêuticos (PADRÃO UCB e COMPLETO) com assinatura digital + PDF |
| ✅ | Caixas de entrada por perfil (rascunhos do Estagiário · pendentes do Preceptor · solicitações do Admin) |
| ✅ | Dashboard personalizado por perfil de acesso |
| ✅ | Inteligência epidemiológica e gráficos analíticos |
| ✅ | Gestão de áreas clínicas, CIDs e indicadores |
| ✅ | Página de perfil do usuário com troca de senha |
| ✅ | Tema claro / escuro persistente |
| ✅ | Painel de Monitoramento do sistema (runtime + DB + tráfego em tempo real) |

---

<div align="center">
  <br>
  &copy; 2026 Clínica Escola de Fisioterapia — UCB. Todos os direitos reservados.
  <br><br>
  Desenvolvido por <strong>Gustavo Martins Gripaldi</strong> e <strong>João Victor Rodrigues Pinto</strong>
</div>
