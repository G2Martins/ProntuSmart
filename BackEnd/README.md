# ProntuSMART — Backend API

**Production-grade REST API** para gerenciamento de prontuários eletrônicos e acompanhamento de tratamento fisioterapêutico em ambiente clínico-acadêmico.

---

## Visão Geral

ProntuSMART é um sistema de Prontuário Eletrônico (EMR - Electronic Medical Record) desenvolvido para a **Clínica Escola de Fisioterapia da Universidade Católica de Brasília (UCB)**. A plataforma implementa o **método SMART** (Específico, Mensurável, Atingível, Relevante e Temporal) para registro estruturado de metas clínicas, evolução funcional de pacientes e garantia de continuidade de atendimento entre estagiários supervisionados, mantendo a autonomia clínica dos profissionais.

### Características Principais

- ✅ **Autenticação JWT** com suporte a múltiplos perfis de acesso (Estagiário, Docente, Administrador)
- ✅ **API REST RESTful** com versionamento semântico (`/api/v1`)
- ✅ **Validação rigorosa de dados** via Pydantic V2 com type hints completos
- ✅ **Operações assíncronas** em 100% do stack (FastAPI + Motor + MongoDB)
- ✅ **Rastreamento temporal completo** de todas as entidades (timestamps criação/atualização)
- ✅ **Cálculo automático de progresso** de metas baseado em direção de melhora
- ✅ **Imutabilidade de dados clínicos** com soft delete para auditoria
- ✅ **Documentação interativa** via Swagger/OpenAPI

---

## Stack Tecnológico

| Componente | Tecnologia | Versão | Propósito |
|-----------|-----------|--------|-----------|
| **Runtime** | Python | 3.10+ | Linguagem principal |
| **Framework Web** | FastAPI | 0.110.0 | Web framework assíncrono ASGI |
| **Servidor WSGI** | Uvicorn | 0.29.0 | Application server |
| **Driver Async BD** | Motor | 3.6+ | Wrapper MongoDB para AsyncIO |
| **Validação/ODM** | Pydantic | 2.6.3+ | Type validation e serialização |
| **Autenticação** | Python-Jose | 3.3.0 | JWT signing e verification |
| **Hash Senha** | Bcrypt | 4.1.2 | Password hashing criptográfico |
| **Config** | Pydantic Settings | 2.2.1 | Environment-based configuration |
| **Banco de Dados** | MongoDB | 4.4+ | NoSQL document database |

---

## Arquitetura e Organização

A aplicação segue arquitetura **modular em camadas** com separação clara de responsabilidades (SoC), facilitando testes unitários, manutenção e escalabilidade horizontal:

```
BackEnd/
├── src/
│   ├── main.py                              # Entry point FastAPI + CORS middleware + lifespan
│   │
│   ├── api/v1/
│   │   ├── router.py                        # Agregador de rotas versionadas
│   │   └── routes/                          # Endpoints organizados por domínio
│   │       ├── auth.py                      # POST /auth/login, /auth/register
│   │       ├── pacientes.py                 # CRUD de pacientes
│   │       ├── prontuarios.py               # Gerenciamento de prontuários
│   │       ├── metas_smart.py               # Criação e rastreamento de metas SMART
│   │       ├── evolucoes.py                 # Registro de sessões de tratamento
│   │       ├── medicoes.py                  # Captura de medições e cálculo de progresso
│   │       ├── indicadores.py               # Referência e lookup de indicadores clínicos
│   │       ├── admin.py                     # Operações administrativas e seed
│   │
│   ├── core/
│   │   ├── config.py                        # Settings com pydantic-settings + .env
│   │   ├── database.py                      # Motor AsyncIOClient + connection pooling
│   │   └── security.py                      # JWT creation/verification + bcrypt + OAuth2
│   │
│   ├── models/                              # Data models (Pydantic schemas para serialização BSON)
│   │   ├── base.py                          # MongoBaseModel base + PyObjectId converter
│   │   ├── dim_usuario.py                   # Dimensão: Usuários do sistema
│   │   ├── dim_paciente.py                  # Dimensão: Pacientes
│   │   ├── dim_area.py                      # Dimensão: Áreas de tratamento clínico
│   │   ├── dim_cid.py                       # Dimensão: Códigos CID-10
│   │   ├── dim_indicador.py                 # Dimensão: Indicadores funcionais de progresso
│   │   ├── dim_status.py                    # Dimensão: Enums de status (Ativo, Alta, etc)
│   │   ├── fato_prontuario.py               # Fato: Prontuários de pacientes
│   │   ├── fato_meta_smart.py               # Fato: Objetivos SMART traçados
│   │   ├── fato_evolucao.py                 # Fato: Sessões de atendimento (imutável)
│   │   └── fato_medicao.py                  # Fato: Medições de progresso (auditada)
│   │
│   ├── schemas/                             # Schemas de validação (request/response)
│   │   ├── auth.py                          # LoginRequest, TokenResponse
│   │   ├── usuario.py                       # UsuarioCreate, UsuarioResponse
│   │   ├── paciente.py                      # PacienteCreate, PacienteUpdate
│   │   ├── prontuario.py                    # ProntuarioCreate, ProntuarioResponse
│   │   ├── meta_smart.py                    # MetaSMARTCreate, MetaSMARTResponse
│   │   ├── evolucao.py                      # EvolucaoCreate, EvolucaoResponse
│   │   └── medicao.py                       # MedicaoCreate, MedicaoResponse
│   │
│   ├── services/                            # Lógica de negócio (business logic layer)
│   │   ├── auth_service.py                  # Autenticação, registro e autorização
│   │   ├── paciente_service.py              # CRUD pacientes + validações
│   │   ├── prontuario_service.py            # Ciclo de vida do prontuário
│   │   ├── meta_smart_service.py            # Criação + rastreamento de metas
│   │   ├── evolucao_service.py              # Registro de sessões + desnormalização
│   │   ├── medicao_service.py               # Medições + cálculo de progresso
│   │   └── indicador_service.py             # Gerenciamento de indicadores
│   │
│   └── utils/
│       ├── helpers.py                       # calcular_progresso(), gerar_numero_prontuario()
│       └── seed.py                          # Popula dim iniciais + cria docente default
│
├── tests/
│   └── test_auth.py                         # Testes unitários de autenticação
│
├── .env.example                             # Template de variáveis de ambiente
├── .gitignore                               # Exclusões de versionamento
├── requirements.txt                         # Dependências do projeto
└── README.md                                # Este arquivo
```

### Padrão de Dados: Modelo em Estrela (Star Schema)

O banco de dados segue um padrão **dimensional** compatível com Data Warehouse analytics:

- **Dimensões (DIM_\*)**: Tabelas de referência (usuários, pacientes, indicadores, áreas, CIDs)
  - Dados relativamente estáticos
  - Baixa cardinalidade
  - Fácil de indexar

- **Fatos (FATO_\*)**: Tabelas transacionais (prontuários, metas, evoluções, medições)
  - Eventos e transações clínicas
  - Crescem continuamente
  - Conectam-se às dimensões via foreign keys

**Benefícios**: Fácil análise agregada, rastreamento completo de eventos, separação clara entre referência e transação, otimização de queries.

---

## Pré-Requisitos de Sistema

- **Python 3.10+** instalado e disponível no PATH
- **MongoDB 4.4+** (Atlas Cloud ☁️ ou instalação local 🖥️)
  - Connection string com credenciais válidas
  - Database criado e acessível
  - Recomenda-se whitelist de IP para segurança
- **pip** (gerenciador de pacotes Python)
- **Git** (opcional, para controle de versão)

---

## Instalação e Configuração

### 1. Navegue até o diretório

```bash
cd BackEnd
```

### 2. Crie e Ative o Ambiente Virtual Python

**Windows (PowerShell/CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Seu prompt deve mudar para indicar que o ambiente está ativo: `(venv) $`

### 3. Instale Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure Variáveis de Ambiente

Crie um arquivo `.env` na raiz de `BackEnd/`. Use `.env.example` como template:

```env
PROJECT_NAME="ProntuSMART API"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# MongoDB (connection string com credenciais)
# Formato: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_URL="mongodb+srv://seu_usuario:sua_senha@seu_cluster.mongodb.net"
DATABASE_NAME="prontusmart_db"

# Segurança (gere uma chave forte com: openssl rand -hex 32)
# Exemplo: openssl rand -hex 32 → 7f8a9c3b1e2d4f6a9c3b1e2d4f6a9c3b1e2d4f6a
SECRET_KEY="sua_chave_secreta_criptografica_com_minimo_32_caracteres"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

**⚠️ Importante**: Adicione `.env` ao `.gitignore` para não versionizar credenciais.

### 5. Inicialize o Banco de Dados

Execute o seed para popular dimensões e criar o **Docente Admin** padrão:

```bash
python -m src.utils.seed
```

Saída esperada:
```
Populando dimensões (Áreas, Indicadores, Status)...
Criando Docente Administrador padrão (matrícula: admin, senha: admin123)...
Seed concluído com sucesso!
```

### 6. Inicie o Servidor

```bash
# Modo desenvolvimento (com hot-reload ativado)
uvicorn src.main:app --reload

# Modo produção (sem reload, com workers)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

Servidor estará disponível em **http://localhost:8000**

---

## API Endpoints Principais

### Autenticação

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|----------------|
| `POST` | `/api/v1/auth/login` | Autenticar via matrícula + senha | ❌ Pública |
| `POST` | `/api/v1/auth/register` | Registrar novo usuário | ✅ Admin only |

**Exemplo: POST /auth/login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Pacientes

| Método | Rota | Descrição | Perfil |
|--------|------|-----------|--------|
| `GET` | `/api/v1/pacientes` | Listar pacientes ativos (paginado) | Estagiário+ |
| `POST` | `/api/v1/pacientes` | Cadastrar novo paciente | Docente+ |
| `GET` | `/api/v1/pacientes/{id}` | Obter paciente por ID | Estagiário+ |
| `PATCH` | `/api/v1/pacientes/{id}` | Atualizar dados cadastrais | Docente+ |

**Exemplo: GET /pacientes/{id}**
```json
{
  "_id": "65f7a8c3d4e2f1a9b8c7d6e5",
  "nome_completo": "João Silva Santos",
  "cpf": "12345678901",
  "data_nascimento": "1985-03-15",
  "genero": "M",
  "telefone": "61987654321",
  "email": "joao@example.com",
  "endereco": "Rua ABC, 123, Brasília-DF",
  "is_ativo": true,
  "criado_em": "2025-03-18T10:30:00Z",
  "atualizado_em": "2025-03-18T10:30:00Z"
}
```

### Prontuários

| Método | Rota | Descrição | Perfil |
|--------|------|-----------|--------|
| `POST` | `/api/v1/prontuarios` | Abrir novo prontuário | Docente+ |
| `GET` | `/api/v1/prontuarios/{id}` | Recuperar prontuário | Estagiário+ |
| `GET` | `/api/v1/prontuarios?paciente_id=...` | Listar prontuários do paciente | Estagiário+ |

**Exemplo: POST /prontuarios**
```json
{
  "paciente_id": "65f7a8c3d4e2f1a9b8c7d6e5",
  "area_id": "65f49e1a2b3c4d5e6f7a8b9c",
  "resumo_avaliacao_inicial": "Paciente chegou com queixa de dor lombar aguda após trauma. Mobilidade reduzida em flexão anterior. Teste de Lasègue positivo à esquerda..."
}
```

**Response:**
```json
{
  "_id": "65f7b9d4e5f3g2c1k9l8m7n6",
  "numero_prontuario": "UCB-2025-00042",
  "paciente_id": "65f7a8c3d4e2f1a9b8c7d6e5",
  "area_id": "65f49e1a2b3c4d5e6f7a8b9c",
  "status": "ATIVO",
  "total_sessoes": 0,
  "data_ultima_evolucao": null,
  "resumo_avaliacao_inicial": "Paciente chegou com queixa de dor lombar...",
  "criado_em": "2025-03-18T10:45:00Z"
}
```

### Metas SMART

| Método | Rota | Descrição | Perfil |
|--------|------|-----------|--------|
| `POST` | `/api/v1/metas-smart` | Criar nova meta SMART | Docente+ |
| `GET` | `/api/v1/metas-smart/{id}` | Recuperar meta | Estagiário+ |
| `GET` | `/api/v1/metas-smart?prontuario_id=...` | Listar metas do prontuário | Estagiário+ |

**Exemplo: POST /metas-smart**
```json
{
  "prontuario_id": "65f7b9d4e5f3g2c1k9l8m7n6",
  "indicador_id": "65f49e2b3c4d5e6f7a8b9c0d",
  "especifico": "Aumentar força muscular do quadríceps L4-L5",
  "valor_inicial": 3.0,
  "valor_alvo": 5.0,
  "alcancavel": "Paciente tem capacidade motora preservada. Teste manual indicou possibilidade de ganho 2 graus",
  "relevante": "Melhora da marcha, redução de quedas, independência funcional para atividades de vida diária",
  "data_limite": "2025-06-18"
}
```

**Response:**
```json
{
  "_id": "65f7cab5f6g4h3d2l1m0n9o8",
  "prontuario_id": "65f7b9d4e5f3g2c1k9l8m7n6",
  "indicador_id": "65f49e2b3c4d5e6f7a8b9c0d",
  "estagiario_id": "65f7a1c2d3e4f5g6h7i8j9k0",
  "especifico": "Aumentar força muscular do quadríceps L4-L5",
  "valor_inicial": 3.0,
  "valor_alvo": 5.0,
  "alcancavel": "Paciente tem capacidade motora preservada...",
  "relevante": "Melhora da marcha, redução de quedas...",
  "data_limite": "2025-06-18T00:00:00Z",
  "status": "EM_ANDAMENTO",
  "progresso_percentual": 0.0,
  "criado_em": "2025-03-18T11:00:00Z"
}
```

### Evoluções (Sessões de Atendimento)

| Método | Rota | Descrição | Perfil | Imutável? |
|--------|------|-----------|--------|-----------|
| `POST` | `/api/v1/evolucoes` | Registrar nova sessão | Estagiário+ | Após criação |
| `GET` | `/api/v1/evolucoes/{id}` | Recuperar evolução | Estagiário+ (própria) | - |
| `GET` | `/api/v1/evolucoes?prontuario_id=...` | Listar histórico | Estagiário+ | - |

**Request: POST /evolucoes**
```json
{
  "prontuario_id": "65f7b9d4e5f3g2c1k9l8m7n6",
  "observacoes_objetivas": "Paciente apresentou redução da espasticidade em membros inferiores. Amplitude de movimento em flexão de quadril aumentou 5 graus (mudou de 70° para 75°). Marcha sem auxílio apresentou melhora qualitativa. Paciência relatou redução de 2 pontos na escala de dor EVA (de 7 para 5).",
  "data_atendimento": "2025-03-18T14:00:00Z"
}
```

**⚠️ Importante**: Evoluções são **imutáveis** (sem edição/exclusão). Para corrigir, crie uma evolução de "Retificação" com novo registro.

---

## Autenticação e Autorização

### Fluxo JWT (JSON Web Tokens)

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ 1. POST /auth/login
       │    (matrícula + senha)
       ▼
┌─────────────────────────┐
│   API Backend FastAPI   │
│ ┌─────────────────────┐ │
│ │ Validar Credenciais │ │
│ │ vs dim_usuario      │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ Gerar JWT com exp. │ │
│ │ sub = user_id      │ │
│ └─────────────────────┘ │
└──────┬──────────────────┘
       │ 2. Response: { access_token, token_type }
       ▼
┌─────────────┐
│  Armazena  │
│   Token     │
│ localStorage│
└──────┬──────┘
       │ 3. Requisições protegidas
       │    Authorization: Bearer <token>
       ▼
┌──────────────────────────┐
│ API Valida Token JWT     │
│ ┌──────────────────────┐ │
│ │ Decode + Verificar  │ │
│ │ Expiração + Assin.  │ │
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ get_current_user()  │ │
│ │ ↓ MongoDB lookup    │ │
│ │ ↓ retorna usuário   │ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

### Configuração JWT

- **Algorithm**: HS256 (HMAC-SHA256)
- **Expiration**: 120 minutos (configurável via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Claim `sub`**: ID do usuário (ObjectId do MongoDB)
- **Refresh**: Não implementado (cliente faz login novamente)

### Perfis de Acesso (RBAC)

| Perfil | Descrição | Permissões |
|--------|-----------|-----------|
| **ADMINISTRADOR** | Gestão sistêmica e técnica | ✅ CRUD usuários, ✅ CRUD parâmetros (dim_*), ✅ Acesso total |
| **DOCENTE** | Supervisão clínica e acadêmica | ✅ CRUD prontuários, ✅ CRUD metas, ✅ Visualizar alunos supervisionados, ✅ Gerar relatórios |
| **ESTAGIÁRIO** | Registro de dados clínicos | ✅ Criar evoluções (próprias), ✅ Criar medições (próprias), ✅ Visualizar prontuários atribuídos |

---

## Modelo de Dados

### Dimensões (Tabelas de Referência)

#### `dim_usuario`
```javascript
{
  "_id": ObjectId,
  "nome_completo": String,              // min 3, max 150
  "matricula": String (unique),          // min 4, max 20
  "email": EmailStr,
  "senha_hash": String,                 // bcrypt hash
  "perfil": Enum["Estagiario", "Docente", "Administrador"],
  "is_ativo": Boolean,                  // Soft delete
  "precisa_trocar_senha": Boolean,      // Força reset on login
  "criado_em": DateTime (UTC),
  "atualizado_em": DateTime (UTC)
}
```

#### `dim_paciente`
```javascript
{
  "_id": ObjectId,
  "nome_completo": String,
  "cpf": String (unique),
  "data_nascimento": Date,
  "genero": Enum["M", "F", "Outro"],
  "telefone": String,
  "email": EmailStr,
  "endereco": String,
  "is_ativo": Boolean,                  // Soft delete
  "criado_em": DateTime (UTC),
  "atualizado_em": DateTime (UTC)
}
```

#### `dim_area`
```javascript
{
  "_id": ObjectId,
  "nome": String (unique),             // Ex: "Fisioterapia Ortopédica"
  "descricao": String,
  "is_ativo": Boolean,
  "criado_em": DateTime (UTC)
}
```

#### `dim_indicador`
```javascript
{
  "_id": ObjectId,
  "nome": String (unique),             // Ex: "Força Muscular", "Dor EVA"
  "descricao": String,
  "unidade": String,                   // Ex: "graus", "pontos", "kg"
  "direcao_melhora": Enum["MAIOR_MELHOR", "MENOR_MELHOR"],
  "valor_minimo": Float,
  "valor_maximo": Float,
  "is_ativo": Boolean,
  "criado_em": DateTime (UTC)
}
```

### Fatos (Tabelas Transacionais)

#### `fato_prontuario`
```javascript
{
  "_id": ObjectId,
  "numero_prontuario": String (unique),  // Formato: UCB-YYYY-ZZZZZ
  "paciente_id": ObjectId (ref: dim_paciente),
  "area_id": ObjectId (ref: dim_area),
  "status": Enum["ATIVO", "ALTA", "INTERROMPIDO"],
  "total_sessoes": Integer,             // Desnormalizado (atualizado em cada evolução)
  "data_ultima_evolucao": DateTime,     // Desnormalizado
  "resumo_avaliacao_inicial": String,
  "criado_em": DateTime (UTC),
  "atualizado_em": DateTime (UTC)
}
```

#### `fato_meta_smart`
```javascript
{
  "_id": ObjectId,
  "prontuario_id": ObjectId (ref: fato_prontuario),
  "indicador_id": ObjectId (ref: dim_indicador),
  "estagiario_id": ObjectId (ref: dim_usuario, quem criou),
  
  // Estrutura SMART (5 componentes)
  "especifico": String,                // S - O quê será alcançado
  "valor_inicial": Float,              // M - Base mensurável
  "valor_alvo": Float,                 // M - Alvo mensurável
  "alcancavel": String,                // A - Por que é realista
  "relevante": String,                 // R - Importância funcional
  "data_limite": DateTime,             // T - Prazo
  
  "status": Enum["EM_ANDAMENTO", "ALCANÇADA", "NÃO_ALCANÇADA"],
  "progresso_percentual": Float,       // 0-100 (atualizado a cada medição)
  "criado_em": DateTime (UTC),
  "atualizado_em": DateTime (UTC)
}
```

#### `fato_evolucao`
```javascript
{
  "_id": ObjectId,
  "prontuario_id": ObjectId (ref: fato_prontuario),
  "estagiario_id": ObjectId (ref: dim_usuario),
  "observacoes_objetivas": String,    // Descrição funcional (sem técnicas)
  "data_atendimento": DateTime,
  "criado_em": DateTime (UTC),
  "atualizado_em": DateTime (UTC)     // NUNCA muda (imutável)
}
```

#### `fato_medicao`
```javascript
{
  "_id": ObjectId,
  "meta_smart_id": ObjectId (ref: fato_meta_smart),
  "estagiario_id": ObjectId (ref: dim_usuario),
  "valor_medido": Float,
  "data_medicao": DateTime,
  "observacoes": String (opcional),
  "criado_em": DateTime (UTC)
}
```

---

## Fórmulas e Cálculos

### Cálculo de Progresso de Meta

Implementado em [src/utils/helpers.py](src/utils/helpers.py), calcula o percentual de progresso em relação à direção de melhora:

**Para MAIOR_MELHOR** (ex: força muscular, mobilidade):
$$P = \min\left(100, \frac{V_{atual} - V_{inicial}}{V_{alvo} - V_{inicial}} \times 100\right)$$

**Para MENOR_MELHOR** (ex: dor, espasticidade):
$$P = \min\left(100, \frac{V_{inicial} - V_{atual}}{V_{inicial} - V_{alvo}} \times 100\right)$$

**Exemplo 1** (Força - MAIOR_MELHOR):
- Inicial: 2.0, Alvo: 5.0, Atual: 3.5
- P = (3.5 - 2.0) / (5.0 - 2.0) × 100 = **50%**

**Exemplo 2** (Dor EVA - MENOR_MELHOR):
- Inicial: 8, Alvo: 2, Atual: 5
- P = (8 - 5) / (8 - 2) × 100 = **50%**

### Geração de Número de Prontuário

Formato: **UCB-YYYY-ZZZZZ**

- `UCB` = Instituição (Universidade Católica de Brasília)
- `YYYY` = Ano corrente (ex: 2025)
- `ZZZZZ` = Sequencial zero-padded de 5 dígitos (ex: 00001, 00042, 10234)

**Exemplos**: `UCB-2025-00001`, `UCB-2026-00042`

Implementado em [src/utils/helpers.py](src/utils/helpers.py#L1).

---

## Padrões de Código

### 1. Imutabilidade de Dados Clínicos

**Evoluções** e **Medições** representam eventos no tempo e são **legalmente imutáveis** em EMR:

```python
# ✅ PERMITIDO: Criar nova evolução
POST /api/v1/evolucoes { prontuario_id, observacoes_objetivas }

# ❌ PROIBIDO: Editar evolução existente
PATCH /api/v1/evolucoes/{id}

# ❌ PROIBIDO: Deletar evolução
DELETE /api/v1/evolucoes/{id}

# ✅ ALTERNATIVA: Criar evolução de "Retificação"
POST /api/v1/evolucoes { 
  prontuario_id, 
  observacoes_objetivas: "RETIFICAÇÃO: A observação anterior deveria ler...",
  data_atendimento: "mesma data"
}
```

### 2. Soft Delete para Dados Cadastrais

Para pacientes e usuários, evitamos DELETE físico (incompatível com auditoria):

```python
# ✅ CORRETO: Soft delete
PATCH /api/v1/pacientes/{id} { is_ativo: False }

# ❌ ERRADO: Hard delete
DELETE /api/v1/pacientes/{id}

# Resultado: Paciente desaparece das buscas mas histórico permanece
SELECT * FROM dim_paciente WHERE is_ativo = True  # Não aparece
SELECT * FROM fato_prontuario 
  WHERE paciente_id = ObjectId(...)              # Histórico intacto
```

### 3. Validação com Pydantic V2

Todos os schemas usam `BaseModel` com type hints completos:

```python
from pydantic import BaseModel, Field, EmailStr

class UsuarioCreate(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    matricula: str = Field(..., min_length=4, max_length=20, 
                          description="Matrícula institucional única")
    email: EmailStr = Field(..., description="E-mail válido")
    senha: str = Field(..., min_length=8)
    perfil: TipoPerfil = Field(default=TipoPerfil.ESTAGIARIO)

    class Config:
        json_schema_extra = {
            "example": {
                "nome_completo": "João Silva",
                "matricula": "202412345",
                "email": "joao@ucb.br",
                "senha": "Senha@Forte123",
                "perfil": "Estagiario"
            }
        }
```

### 4. Async/Await em 100% do Stack

FastAPI + Motor (AsyncIO MongoDB driver):

```python
from fastapi import Depends
from src.core.database import get_database

async def buscar_paciente(
    paciente_id: str, 
    db = Depends(get_database)
):
    paciente = await db.dim_paciente.find_one(
        {"_id": ObjectId(paciente_id)}
    )
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente
```

### 5. Conversão ObjectId → String JSON

MongoDB nativo retorna `ObjectId`, Pydantic serializa para string JSON:

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Optional
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )
```

---

## Documentação Interativa (Swagger)

Com o servidor rodando, acesse:

| Interface | URL | Descrição |
|-----------|-----|-----------|
| **Swagger UI** | http://localhost:8000/docs | Testa endpoints interativamente |
| **ReDoc** | http://localhost:8000/redoc | Documentação offline formatada |
| **OpenAPI JSON** | http://localhost:8000/api/v1/openapi.json | Schema em JSON puro |

**Para testar autenticado no Swagger**:
1. Clique no botão **"Authorize"** (cadeado no topo)
2. Digite o token JWT retornado de `/auth/login`
3. Clique "Authorize" e feche o diálogo
4. Todos os endpoints protegidos agora funcionarão

---

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| `ConnectionError: Failed to connect to MongoDB` | Credenciais inválidas ou rede bloqueada | Verifique `MONGODB_URL`, IP whitelist, conexão de rede |
| `401 Unauthorized` | Token expirado ou inválido | Re-autentique via `/auth/login` |
| `ValidationError: invalid type for field` | Schema JSON não bate com Pydantic | Consulte `/docs` (Swagger) para estrutura esperada |
| `"Matrícula já cadastrada"` | Tentativa registrar usuário duplicado | Escolha matrícula diferente |
| `ModuleNotFoundError: No module named 'motor'` | Dependências não instaladas | Execute `pip install -r requirements.txt` |
| `BSON decode error in connection pool` | Problema com constring do MongoDB | Teste a URI em ferramentas como MongoDB Compass |

---

## Testing

Execute testes unitários:

```bash
# Instale pytest (se não tiver)
pip install pytest pytest-asyncio

# Rode todos os testes
pytest tests/ -v --tb=short

# Rode teste específico
pytest tests/test_auth.py -v
```

---

## Roadmap Futuro

- [ ] Integração com e-signature (assinatura digital de prontuários)
- [ ] Exportação de prontuários em PDF com branding UCB
- [ ] Relatórios avançados (Plotly, ReportLab)
- [ ] Notificações via Webhook para eventos clínicos
- [ ] Rate limiting (FastAPI-Limiter) e caching (Redis)
- [ ] Testes de carga (k6, Locust)
- [ ] API de BI/Analytics para dashboards
- [ ] Integração com sistemas PACS (radiologia)

---

## Referências e Recursos

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Pydantic V2**: https://docs.pydantic.dev/2.0/
- **MongoDB Motor**: https://motor.readthedocs.io/
- **JWT RFC 7519**: https://tools.ietf.org/html/rfc7519
- **Method SMART Goals**: https://www.projectsmart.co.uk/smart-goals.php
- **Web Security (OWASP)**: https://owasp.org/

---

## Suporte e Contribuições

Para dúvidas, issues ou sugestões de melhorias:

1. **Abra uma Issue** no repositório
2. **Faça um Pull Request** com suas melhorias (branches: `feature/`, `fix/`, `docs/`)
3. **Follow commit conventions**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`

---

## Licença

Desenvolvido para a **Clínica Escola de Fisioterapia — Universidade Católica de Brasília (UCB)**

**Versão**: 1.0.0  
**Última atualização**: Março/2025  
**Mantido por**: Equipe de Desenvolvimento UCB
