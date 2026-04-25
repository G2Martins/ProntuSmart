<div align="center">

# ProntuSMART — Backend API

### API REST para o Sistema de Prontuário Eletrônico da Clínica Escola de Fisioterapia — UCB

<br>

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/MongoDB-4.4+-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <br><br>
  <img src="https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Docs-Swagger_UI-85EA2D?style=for-the-badge&logo=swagger&logoColor=black" alt="Swagger">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Async-Motor_3.6+-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="Motor">
</p>

</div>

---

## Sobre

API REST da plataforma ProntuSMART, responsável pela autenticação, controle de acesso por perfil (RBAC), persistência de dados clínicos, geração de relatórios fisioterapêuticos com assinatura digital, registro de testes/escalas funcionais e geração de indicadores analíticos. Construída com FastAPI e MongoDB em arquitetura modular em camadas, garantindo operações assíncronas em todo o stack.

---

## Stack Tecnológico

| Componente | Tecnologia | Versão |
|:---|:---|:---|
| Linguagem | Python | 3.10+ |
| Framework Web | FastAPI | 0.110.0 |
| Servidor ASGI | Uvicorn | 0.29.0 |
| Driver Async BD | Motor | 3.6+ |
| Validação | Pydantic | 2.6.3+ |
| Autenticação | python-jose (JWT) | 3.3.0 |
| Hash de Senha | bcrypt | 4.1.2 |
| Geração de PDF | ReportLab | — |
| Banco de Dados | MongoDB | 4.4+ |

---

## Instalação e Configuração

### 1. Pré-requisitos
- Python 3.10+ instalado e disponível no PATH
- MongoDB 4.4+ (local ou Atlas Cloud)
- pip (gerenciador de pacotes Python)

### 2. Ambiente Virtual

**Windows:**
```bash
cd BackEnd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
cd BackEnd
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependências
```bash
pip install -r requirements.txt
```

### 4. Variáveis de Ambiente

Crie um arquivo `.env` na raiz de `BackEnd/` com base no `.env.example`:

```env
PROJECT_NAME="ProntuSMART API"
VERSION="1.0.0"
API_V1_STR="/api/v1"

MONGODB_URL="mongodb+srv://usuario:senha@cluster.mongodb.net"
DATABASE_NAME="prontusmart_db"

SECRET_KEY="sua_chave_secreta_com_minimo_32_caracteres"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

> **Importante:** Nunca versione o arquivo `.env`. Ele já está no `.gitignore`.

### 5. Seed do Banco de Dados

Popula áreas clínicas, indicadores e cria três contas-base. **Não cria pacientes** — o banco fica pronto para uso real, sem dados fictícios. A coleção `dim_cid` é preservada (base oficial CID-10).

```bash
python -m src.utils.seed
```

Contas criadas pela seed (todas com senha `ucb@1234`):

| Matrícula | Nome | Perfil | Área |
|:---|:---|:---|:---|
| `admin01` | Administrador Sistema | Administrador | — |
| `prec01`  | Velluma | Preceptor (Docente) | Neurologia Adulto |
| `est01`   | Emellyn Lima | Estagiária | Neurologia Adulto |

### 6. Iniciar o Servidor

```bash
uvicorn src.main:app --reload
```

API disponível em **`http://localhost:8000`**
Documentação Swagger em **`http://localhost:8000/docs`**

---

## Arquitetura de Pastas

```
BackEnd/
│
├── src/
│   │
│   ├── main.py                       # FastAPI bootstrap, middleware de métricas, CORS, lifespan
│   │
│   ├── API/
│   │   └── v1/
│   │       ├── router.py             # Agrega routers de domínio sob /api/v1
│   │       └── routes/
│   │           ├── auth.py           # Login, /auth/me, troca de senha, /auth/registrar (público)
│   │           ├── pacientes.py      # CRUD de pacientes
│   │           ├── prontuarios.py    # Triagem (apenas Estagiário) e visão de prontuários
│   │           ├── evolucoes.py      # Sessões de atendimento + revisão pelo Preceptor
│   │           ├── metas_smart.py    # CRUD de metas SMART
│   │           ├── medicoes.py       # Registro de medições e progresso
│   │           ├── indicadores.py    # CRUD de indicadores clínicos
│   │           ├── areas.py          # Áreas clínicas
│   │           ├── cids.py           # Códigos CID-10
│   │           ├── dashboard.py      # Inteligência epidemiológica
│   │           ├── relatorios.py     # Relatórios fisioterapêuticos com assinatura digital + PDF
│   │           ├── testes.py         # Testes/escalas: Avaliação Funcional, Sunny, Mini-BESTest
│   │           └── admin.py          # Gestão de usuários, solicitações de cadastro e monitoramento
│   │
│   ├── core/
│   │   ├── config.py                 # Variáveis de ambiente via pydantic-settings
│   │   ├── database.py               # Conexão Motor com MongoDB (lifespan async)
│   │   ├── security.py               # JWT + bcrypt + dependency get_current_user
│   │   └── monitor.py                # RuntimeMonitor: métricas em memória (uptime, RPS, P95, erros)
│   │
│   ├── models/                       # Modelos Pydantic / BSON
│   │   ├── base.py                   # MongoBaseModel: ObjectId↔string, timestamps
│   │   ├── dim_usuario.py            # Estagiário, Docente (Preceptor), Administrador
│   │   ├── dim_paciente.py
│   │   ├── dim_area.py
│   │   ├── dim_cid.py                # Base oficial CID-10 (preservada na seed)
│   │   ├── dim_indicador.py          # Limites mín/máx + direção de melhora
│   │   ├── dim_status.py             # Enums de status (prontuário, meta, evolução)
│   │   ├── dim_solicitacao.py        # Solicitação pública de cadastro com fluxo de aprovação
│   │   ├── fato_prontuario.py        # Triagem + Avaliação Funcional + Síntese
│   │   ├── fato_meta_smart.py
│   │   ├── fato_evolucao.py
│   │   ├── fato_medicao.py
│   │   ├── fato_relatorio.py         # Relatórios com tipos PADRÃO/COMPLETO + assinaturas digitais
│   │   └── fato_teste.py             # Testes/escalas aplicadas ao paciente (genérico por tipo)
│   │
│   ├── schemas/                      # Validação request/response
│   │   ├── auth.py
│   │   ├── usuario.py
│   │   ├── paciente.py
│   │   ├── prontuario.py
│   │   ├── evolucao.py
│   │   ├── meta_smart.py
│   │   ├── medicao.py
│   │   ├── indicador.py
│   │   ├── area.py
│   │   ├── cid.py
│   │   ├── relatorio.py
│   │   ├── teste.py
│   │   └── solicitacao.py
│   │
│   ├── services/                     # Lógica de negócio desacoplada dos endpoints
│   │   ├── auth_service.py
│   │   ├── paciente_service.py
│   │   ├── prontuario_service.py
│   │   ├── evolucao_service.py
│   │   ├── meta_smart_service.py
│   │   ├── medicao_service.py
│   │   ├── indicador_service.py
│   │   ├── indicador_limits.py       # Validação de limites mín/máx por indicador
│   │   ├── dashboard_service.py
│   │   └── relatorio_pdf_service.py  # Geração de PDF (PADRÃO modelo UCB e COMPLETO)
│   │
│   └── utils/
│       ├── helpers.py
│       └── seed.py                   # Seed enxuta: áreas + indicadores + 3 contas (sem pacientes)
│
├── tests/
│   └── test_auth.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Modelo de Dados: Esquema em Estrela

O banco segue um padrão **dimensional** que separa referências de transações:

- **Dimensões (`dim_*`)** — Dados de referência relativamente estáticos: usuários, pacientes, áreas, CIDs, indicadores, solicitações de cadastro. Baixa cardinalidade, alta reutilização.
- **Fatos (`fato_*`)** — Eventos clínicos que crescem continuamente: prontuários, metas, evoluções, medições, relatórios e testes aplicados.

> Nota: o enum interno do perfil docente é `Docente` (preservado por compatibilidade no banco), mas a interface exibe sempre o termo **Preceptor**, que é como a clínica chama o supervisor.

---

## Endpoints Principais

### Autenticação e Cadastro
| Método | Rota | Descrição | Acesso |
|:---|:---|:---|:---|
| `POST` | `/api/v1/auth/login` | Login com matrícula e senha, retorna JWT | Público |
| `POST` | `/api/v1/auth/registrar` | Submete solicitação pública de cadastro (passa por aprovação do Admin) | Público |
| `GET`  | `/api/v1/auth/me` | Retorna dados do usuário autenticado | Autenticado |
| `POST` | `/api/v1/auth/trocar-senha` | Troca de senha temporária para definitiva | Autenticado |

### Pacientes e Prontuários
| Método | Rota | Descrição | Acesso |
|:---|:---|:---|:---|
| `GET`  | `/api/v1/pacientes` | Listar pacientes (com busca) | Autenticado |
| `POST` | `/api/v1/pacientes` | Cadastrar novo paciente | Autenticado |
| `POST` | `/api/v1/prontuarios` | **Triagem** — abrir prontuário | **Apenas Estagiário** |
| `GET`  | `/api/v1/prontuarios/meus` | Lista por perfil (Estagiário vê seus + da área) | Autenticado |
| `GET`  | `/api/v1/prontuarios/{id}` | Visão completa do prontuário | Autenticado |
| `PATCH`| `/api/v1/prontuarios/{id}/avaliacao` | Atualiza avaliação funcional + síntese | Estagiário |

### Evoluções, Metas e Medições
| Método | Rota | Descrição |
|:---|:---|:---|
| `POST`  | `/api/v1/evolucoes` | Registrar sessão (estagiário) |
| `PATCH` | `/api/v1/evolucoes/{id}/revisar` | Aprovar / devolver evolução (Preceptor) |
| `GET`   | `/api/v1/evolucoes/pendentes/count` | Contagem de evoluções pendentes |
| `POST`  | `/api/v1/metas-smart` | Criar meta SMART |
| `POST`  | `/api/v1/medicoes` | Registrar medição e atualizar progresso |

### Relatórios Fisioterapêuticos
| Método | Rota | Descrição |
|:---|:---|:---|
| `POST`  | `/api/v1/relatorios` | Criar rascunho (PADRÃO escolhe Preceptor designado) |
| `GET`   | `/api/v1/relatorios/meus` | Listar relatórios respeitando RBAC |
| `GET`   | `/api/v1/relatorios/docentes-disponiveis/{prontuario_id}` | Sugerir Preceptores que já revisaram evoluções |
| `POST`  | `/api/v1/relatorios/{id}/assinar` | Assinatura digital com reentrada de senha + hash SHA256 |
| `GET`   | `/api/v1/relatorios/{id}/pdf` | Streaming do PDF (PADRÃO ou COMPLETO) |
| `DELETE`| `/api/v1/relatorios/{id}` | Cancela rascunho |

### Testes e Escalas
| Método | Rota | Descrição |
|:---|:---|:---|
| `POST`  | `/api/v1/testes` | Aplicar teste (Avaliação Funcional / Sunny / MiniBest) |
| `GET`   | `/api/v1/testes/prontuario/{prontuario_id}` | Histórico de testes do prontuário |
| `GET`   | `/api/v1/testes/{id}` | Detalhes de um teste |
| `PATCH` | `/api/v1/testes/{id}` | Editar teste (apenas o autor) |
| `DELETE`| `/api/v1/testes/{id}` | Excluir teste |

### Administração
| Método | Rota | Descrição |
|:---|:---|:---|
| `GET`    | `/api/v1/admin/estatisticas` | KPIs leves para dashboard do Admin |
| `GET`    | `/api/v1/admin/monitoramento` | Snapshot completo: runtime, tráfego, banco, negócio, autenticação |
| `GET`    | `/api/v1/admin/usuarios` | Listar usuários com filtros |
| `POST`   | `/api/v1/admin/usuarios` | Criar usuário (manual) |
| `PUT`    | `/api/v1/admin/usuarios/{id}` | Atualizar usuário |
| `PATCH`  | `/api/v1/admin/usuarios/{id}/reset-password` | Reset com troca obrigatória no próximo login |
| `GET`    | `/api/v1/admin/solicitacoes` | Caixa de entrada de cadastros pendentes |
| `PATCH`  | `/api/v1/admin/solicitacoes/{id}/aprovar` | Aprovar (com edição opcional) e criar usuário |
| `PATCH`  | `/api/v1/admin/solicitacoes/{id}/recusar` | Recusar com motivo |

---

## Autenticação e Controle de Acesso

### Perfis (RBAC)

| Perfil | Permissões Principais |
|:---|:---|
| **Administrador** | CRUD de usuários, áreas, CIDs, indicadores; aprovação de solicitações de cadastro; monitoramento profundo do sistema |
| **Preceptor** (enum interno: `Docente`) | Supervisiona estagiários, revisa e coassina evoluções, assina relatórios padrão |
| **Estagiário** | **Faz triagem** (criação de prontuário), registra evoluções/medições/testes nos seus prontuários e da sua área |

### Fluxo JWT
1. `POST /auth/login` retorna `access_token` (HS256, 120 min de validade).
2. O cliente envia em cada requisição: `Authorization: Bearer <token>`.
3. O backend decodifica, busca o usuário no MongoDB e injeta como dependência via `get_current_user`.

### Fluxo de Cadastro Público
1. Usuário envia `POST /auth/registrar` com seus dados — gera registro `Pendente` em `dim_solicitacao_cadastro`.
2. Admin visualiza a solicitação na caixa de entrada do painel.
3. Admin pode **editar** os campos antes de aprovar — ao aprovar, gera o `DimUsuario` definitivo.
4. Em caso de recusa, o motivo fica registrado para auditoria.

---

## Monitoramento

O endpoint `GET /admin/monitoramento` retorna um snapshot agregado em tempo real:

- **Runtime:** uptime da API, versão do Python, plataforma, arquitetura.
- **Tráfego HTTP:** total de requisições, P95 / P99, RPS, distribuição por status (2xx/3xx/4xx/5xx), por método, top endpoints, endpoints mais lentos, últimas requisições, últimos erros.
- **Banco MongoDB:** versão, uptime, conexões ativas/disponíveis, opcounters, memória residente/virtual, bytes I/O, tamanho de dados/storage/índices, lista detalhada de coleções com contagem de documentos.
- **Negócio:** solicitações de cadastro pendentes, evoluções pendentes de revisão, relatórios em trânsito, contagem de usuários por perfil.
- **Autenticação:** logins de sucesso vs falha, taxa de sucesso.

As métricas de tráfego são coletadas pelo middleware HTTP em `core/monitor.py` (em memória — reseta a cada restart).

---

## Documentação Interativa

Com o servidor rodando, acesse:

| Interface | URL |
|:---|:---|
| **Swagger UI** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |

Para testar endpoints autenticados no Swagger: clique em **Authorize**, cole o token JWT retornado pelo login e confirme.

---

## Troubleshooting

| Problema | Causa Provável | Solução |
|:---|:---|:---|
| `Failed to connect to MongoDB` | Connection string inválida ou IP não liberado | Verifique `MONGODB_URL` e o IP whitelist no Atlas |
| `401 Unauthorized` | Token expirado ou ausente | Re-autentique via `/auth/login` |
| `403 Forbidden` na triagem | Apenas Estagiário pode triar | Faça login com perfil Estagiário |
| `422 Unprocessable Entity` | Payload não passa na validação Pydantic | Consulte o Swagger (`/docs`) para a estrutura esperada |
| `ModuleNotFoundError` | Dependências não instaladas | Execute `pip install -r requirements.txt` com o venv ativo |
| Solicitação pendente duplicada | Já existe solicitação pendente com mesma matrícula/email | Aguarde o Admin processar a anterior |

---

<div align="center">
  <br>
  &copy; 2026 Clínica Escola de Fisioterapia — UCB. Todos os direitos reservados.
  <br><br>
  Desenvolvido por <strong>Gustavo Martins Gripaldi</strong> e <strong>João Victor Rodrigues Pinto</strong>
</div>
