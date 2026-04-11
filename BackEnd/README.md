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

API REST da plataforma ProntuSMART, responsável pela autenticação, controle de acesso por perfil (RBAC), persistência de dados clínicos e geração de indicadores analíticos. Construída com FastAPI e MongoDB em arquitetura modular em camadas, garantindo operações assíncronas em 100% do stack.

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

Popula as dimensões iniciais (áreas, indicadores, status) e cria o usuário administrador padrão:

```bash
python -m src.utils.seed
```

Credenciais padrão geradas: **matrícula:** `admin` | **senha:** `admin123`

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
├── src/                          # Código-fonte principal
│   │
│   ├── main.py                   # Entry point: instancia FastAPI, registra routers e configura CORS
│   │
│   ├── API/
│   │   └── v1/
│   │       ├── router.py         # Agrega todos os routers de domínio sob o prefixo /api/v1
│   │       └── routes/           # Endpoints organizados por domínio de negócio
│   │           ├── auth.py       # Login, registro de usuários e endpoint GET /auth/me
│   │           ├── pacientes.py  # CRUD de pacientes (busca, cadastro, edição, soft delete)
│   │           ├── prontuarios.py # Abertura, listagem e visão completa de prontuários
│   │           ├── evolucoes.py  # Registro imutável de sessões de atendimento
│   │           ├── metas_smart.py # Criação e rastreamento de metas SMART por prontuário
│   │           ├── medicoes.py   # Registro de medições e cálculo automático de progresso
│   │           ├── indicadores.py # CRUD de indicadores clínicos (admin) e lookup público
│   │           ├── areas.py      # Gestão de áreas clínicas (ortopedia, neurologia, etc.)
│   │           ├── cids.py       # Gestão de códigos CID-10 para diagnósticos
│   │           ├── dashboard.py  # Endpoints de analytics e inteligência epidemiológica
│   │           └── admin.py      # Operações administrativas: estatísticas e gestão de usuários
│   │
│   ├── core/                     # Infraestrutura central compartilhada por toda a aplicação
│   │   ├── config.py             # Leitura e validação das variáveis de ambiente via pydantic-settings
│   │   ├── database.py           # Conexão assíncrona com MongoDB via Motor (connection pooling)
│   │   └── security.py           # Criação e verificação de JWT, hash bcrypt, OAuth2PasswordBearer
│   │
│   ├── models/                   # Modelos de dados Pydantic para serialização BSON ↔ JSON
│   │   ├── base.py               # MongoBaseModel: converte ObjectId para string, define timestamps
│   │   ├── dim_usuario.py        # Dimensão de usuários (estagiários, docentes, administradores)
│   │   ├── dim_paciente.py       # Dimensão de pacientes atendidos pela clínica
│   │   ├── dim_area.py           # Dimensão de áreas clínicas (ex: Fisioterapia Ortopédica)
│   │   ├── dim_cid.py            # Dimensão de códigos diagnósticos CID-10
│   │   ├── dim_indicador.py      # Dimensão de indicadores funcionais (força, dor EVA, etc.)
│   │   ├── dim_status.py         # Enums de status: perfis de usuário, status de prontuário e meta
│   │   ├── fato_prontuario.py    # Fato: prontuário do paciente (número UCB, sessões, status)
│   │   ├── fato_meta_smart.py    # Fato: metas SMART com 5 componentes e progresso calculado
│   │   ├── fato_evolucao.py      # Fato: registro imutável de cada sessão de atendimento
│   │   └── fato_medicao.py       # Fato: medição de indicador vinculada a uma meta SMART
│   │
│   ├── schemas/                  # Schemas de validação de entrada e saída (request/response)
│   │   ├── auth.py               # LoginRequest, TokenResponse, schemas de troca de senha
│   │   ├── usuario.py            # UsuarioCreate, UsuarioUpdate, UsuarioResponse
│   │   ├── paciente.py           # PacienteCreate, PacienteUpdate, PacienteResponse
│   │   ├── prontuario.py         # ProntuarioCreate, ProntuarioResponse (com dados desnormalizados)
│   │   ├── evolucao.py           # EvolucaoCreate, EvolucaoResponse
│   │   ├── meta_smart.py         # MetaSMARTCreate, MetaSMARTResponse (com progresso_percentual)
│   │   ├── medicao.py            # MedicaoCreate, MedicaoResponse
│   │   ├── indicador.py          # IndicadorCreate, IndicadorUpdate, IndicadorResponse
│   │   ├── area.py               # AreaCreate, AreaUpdate, AreaResponse
│   │   └── cid.py                # CIDCreate, CIDUpdate, CIDResponse
│   │
│   ├── services/                 # Camada de lógica de negócio (desacoplada dos endpoints)
│   │   ├── auth_service.py       # Autenticação, criação de usuários e verificação de perfil
│   │   ├── paciente_service.py   # CRUD de pacientes com validações (CPF único, soft delete)
│   │   ├── prontuario_service.py # Ciclo de vida do prontuário: abertura, visão completa, alta
│   │   ├── evolucao_service.py   # Criação de evoluções, contagem de pendentes por docente
│   │   ├── meta_smart_service.py # Criação de metas SMART e atualização de status/progresso
│   │   ├── medicao_service.py    # Registro de medições e recalculo de progresso da meta
│   │   ├── indicador_service.py  # CRUD de indicadores com controle de ativação
│   │   └── dashboard_service.py  # Agregações analíticas para dashboards e epidemiologia
│   │
│   └── utils/                    # Utilitários auxiliares
│       ├── helpers.py            # calcular_progresso() por direção de melhora, gerar_numero_prontuario()
│       └── seed.py               # Popula dimensões iniciais e cria o usuário administrador padrão
│
├── tests/
│   └── test_auth.py              # Testes unitários do fluxo de autenticação
│
├── .env.example                  # Template de variáveis de ambiente (não contém credenciais reais)
├── .gitignore                    # Exclui venv/, .env, __pycache__, arquivos gerados
├── requirements.txt              # Lista de dependências Python com versões fixas
└── README.md                     # Este arquivo
```

### Modelo de Dados: Esquema em Estrela

O banco segue um padrão **dimensional** que separa referências de transações:

- **Dimensões (`dim_*`)** — Dados de referência relativamente estáticos (usuários, pacientes, áreas, CIDs, indicadores). Baixa cardinalidade, alta reutilização.
- **Fatos (`fato_*`)** — Eventos e transações clínicas (prontuários, metas, evoluções, medições). Crescem continuamente. Conectam-se às dimensões por ID.

---

## Endpoints Principais

### Autenticação
| Método | Rota | Descrição | Acesso |
|:---|:---|:---|:---|
| `POST` | `/api/v1/auth/login` | Login com matrícula e senha, retorna JWT | Público |
| `POST` | `/api/v1/auth/register` | Registrar novo usuário | Administrador |
| `GET` | `/api/v1/auth/me` | Retorna dados do usuário autenticado | Autenticado |
| `POST` | `/api/v1/auth/trocar-senha` | Troca de senha na sessão | Autenticado |

### Pacientes
| Método | Rota | Descrição | Acesso |
|:---|:---|:---|:---|
| `GET` | `/api/v1/pacientes` | Listar pacientes (com busca por nome/CPF) | Estagiário+ |
| `POST` | `/api/v1/pacientes` | Cadastrar novo paciente | Docente+ |
| `GET` | `/api/v1/pacientes/{id}` | Buscar paciente por ID | Estagiário+ |
| `PATCH` | `/api/v1/pacientes/{id}` | Atualizar dados cadastrais | Docente+ |

### Prontuários
| Método | Rota | Descrição | Acesso |
|:---|:---|:---|:---|
| `POST` | `/api/v1/prontuarios` | Abrir prontuário e vincular estagiário | Docente+ |
| `GET` | `/api/v1/prontuarios/meus` | Listar prontuários do usuário autenticado | Estagiário+ |
| `GET` | `/api/v1/prontuarios/{id}` | Visão completa do prontuário | Estagiário+ |

### Evoluções, Metas e Medições
| Método | Rota | Descrição |
|:---|:---|:---|
| `POST` | `/api/v1/evolucoes` | Registrar sessão de atendimento (imutável após criação) |
| `POST` | `/api/v1/metas-smart` | Criar meta SMART vinculada ao prontuário |
| `POST` | `/api/v1/medicoes` | Registrar medição e recalcular progresso da meta |

---

## Autenticação e Controle de Acesso

### Perfis (RBAC)

| Perfil | Permissões Principais |
|:---|:---|
| **Administrador** | CRUD de usuários, áreas, CIDs, indicadores; acesso a todas as estatísticas |
| **Docente** | Abrir prontuários, vincular estagiários, revisar e assinar evoluções |
| **Estagiário** | Registrar evoluções e medições em seus prontuários vinculados |

### Fluxo JWT
1. `POST /auth/login` retorna `access_token` (HS256, 120 min de validade).
2. O cliente armazena o token e o envia em cada requisição: `Authorization: Bearer <token>`.
3. O backend decodifica o token, busca o usuário no MongoDB e verifica o perfil.

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
| `422 Unprocessable Entity` | Payload não passa na validação Pydantic | Consulte o Swagger (`/docs`) para a estrutura esperada |
| `ModuleNotFoundError` | Dependências não instaladas | Execute `pip install -r requirements.txt` com o venv ativo |
| Matrícula já cadastrada | Tentativa de registro duplicado | Escolha uma matrícula diferente |

---

<div align="center">
  <br>
  &copy; 2026 Clínica Escola de Fisioterapia — UCB. Todos os direitos reservados.
  <br><br>
  Desenvolvido por <strong>Gustavo Martins Gripaldi</strong> e <strong>João Victor Rodrigues Pinto</strong>
</div>
