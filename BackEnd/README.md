# ProntuSMART - API Backend 🚀

Este é o backend do **ProntuSMART**, um sistema de Prontuário Eletrônico desenvolvido para a Clínica Escola de Fisioterapia da Universidade Católica de Brasília (UCB). O sistema foca no registro e acompanhamento da evolução funcional dos pacientes utilizando o **método SMART**, garantindo a continuidade do atendimento entre estagiários sem interferir na autonomia clínica.

A API foi construída com **Python** e **FastAPI**, utilizando **MongoDB** como banco de dados (via `motor` assíncrono) e validação estrita de dados com **Pydantic V2**.

---

## 🏗️ Arquitetura do Projeto

O projeto segue uma arquitetura modular focada em separação de responsabilidades (Rotas, Serviços, Modelos e Schemas):

```text
BackEnd/
├── src/
│   ├── main.py                ← Entry point FastAPI + CORS + lifespan
│   ├── api/
│   │   └── v1/
│   │       ├── router.py      ← Registra todas as rotas em /api/v1
│   │       └── routes/
│   │           ├── auth.py          ← POST /auth/login | /auth/register
│   │           ├── pacientes.py     ← CRUD /pacientes
│   │           ├── prontuarios.py   ← /prontuarios
│   │           ├── metas_smart.py   ← /metas-smart
│   │           ├── evolucoes.py     ← /evolucoes
│   │           └── medicoes.py      ← /medicoes
│   ├── core/
│   │   ├── config.py          ← Settings via pydantic-settings + .env
│   │   ├── database.py        ← Motor async + índices automáticos
│   │   └── security.py        ← JWT, hash senha, get_current_user
│   ├── models/
│   │   ├── base.py            ← MongoBaseModel + PyObjectId (Pydantic v2)
│   │   ├── dim_usuario.py
│   │   ├── dim_paciente.py
│   │   ├── dim_area.py
│   │   ├── dim_cid.py
│   │   ├── dim_indicador.py
│   │   ├── dim_status.py
│   │   ├── fato_prontuario.py
│   │   ├── fato_meta_smart.py
│   │   ├── fato_evolucao.py
│   │   └── fato_medicao.py
│   ├── schemas/
│   │   ├── auth.py / usuario.py
│   │   ├── paciente.py / prontuario.py
│   │   ├── meta_smart.py / evolucao.py / medicao.py
│   ├── services/
│   │   ├── auth_service.py         ← Login + criar usuário
│   │   ├── paciente_service.py     ← CRUD pacientes
│   │   ├── prontuario_service.py   ← Abrir prontuário + contador sessões
│   │   ├── meta_smart_service.py   ← Criar metas SMART + prazo automático
│   │   ├── evolucao_service.py     ← Inserir sessão + atualiza desnorm.
│   │   └── medicao_service.py      ← Registrar medição + calcular progresso
│   └── utils/
│       ├── helpers.py         ← calcular_progresso, gerar_numero
│       └── seed.py            ← Popula dims iniciais + docente padrão
├── tests/
│   └── test_auth.py
├── .env                       ← Variáveis de ambiente reais (Não versionado)
├── .env.example               ← Template de variáveis de ambiente
├── .gitignore
├── README.md
└── requirements.txt           ← Dependências do projeto
```
-- 

## 🛠️ Tecnologias Utilizadas
- Linguagem: Python 3.10+
- Framework Web: FastAPI
- Banco de Dados: MongoDB (via Motor assíncrono e PyMongo)
- Validação: Pydantic V2
- Autenticação: JWT (JSON Web Tokens) com Passlib (Bcrypt)

# 🚀 Como Configurar e Rodar Localmente

> **Aviso:** O desenvolvimento local deste projeto utiliza um ambiente virtual Python (`venv`) tradicional, sem a necessidade de Docker.

***

## 1. Pré-requisitos

- Python instalado na máquina
- Acesso a um cluster MongoDB (como o MongoDB Atlas) com a *connection string* em mãos

***

## 2. Passo a Passo de Instalação

### Passo 1 — Navegue até a pasta do Backend

Abra o terminal e garanta que você está dentro do diretório raiz do backend:

```bash
cd BackEnd
```

***

### Passo 2 — Crie e ative o ambiente virtual (`venv`)

Crie o ambiente virtual para isolar as dependências do projeto:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

***

### Passo 3 — Instale as dependências

Com o `venv` ativado, instale as bibliotecas necessárias listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

***

### Passo 4 — Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz da pasta `BackEnd/` utilizando o `.env.example` como base.  
Substitua os valores reais, especialmente a URL do MongoDB e a Chave Secreta:

```env
PROJECT_NAME="ProntuSMART API"
VERSION="1.0.0"
API_V1_STR="/api/v1"
MONGODB_URL="sua_connection_string_aqui"
DATABASE_NAME="prontusmart_db"
SECRET_KEY="sua_chave_secreta_gerada_aqui"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

***

### Passo 5 — Povoamento Inicial do Banco (Seed)

Antes de subir a aplicação, rode o script de seed para popular as tabelas dimensão (áreas e indicadores) e criar o **Docente Administrador** padrão:

```bash
python -m src.utils.seed
```

***

### Passo 6 — Inicie o Servidor

Rode a aplicação usando o Uvicorn com *hot-reload* ativo (ideal para desenvolvimento):

```bash
uvicorn src.main:app --reload
```

O servidor estará rodando em: **http://localhost:8000**

***

## 📚 Documentação da API (Swagger)

O FastAPI gera a documentação interativa automaticamente. Com o servidor rodando, acesse no seu navegador:

| Interface | URL |
|---|---|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |

> Pelo Swagger, você pode testar o fluxo de autenticação inserindo a matrícula e senha do **Docente Padrão** (criado no Seed) clicando no botão **"Authorize"** no topo da página.


1. Perfil ADMINISTRADOR (Foco Técnico e Operacional)

Gestão de Usuários: CRUD (Criar, Ler, Atualizar, Inativar/Excluir) de Docentes, Estagiários e outros Administradores. Redefinição de senhas.

Gestão de Parâmetros Clínicos (Tabelas Dimensão): É o Admin quem vai adicionar uma nova Área de Atendimento (ex: "Fisioterapia Esportiva") ou cadastrar novos testes no sistema (ex: adicionar o teste "Escala de Berg" em dim_indicador).

Saúde do Sistema e Conectores: Dashboard técnico mostrando se o banco de dados (MongoDB) está online, quantidade total de requisições, armazenamento em disco utilizado

2. Perfil DOCENTE (Foco Estratégico, Acadêmico e Clínico)

Dashboard de Produtividade: Gráficos mostrando o volume de atendimentos por estagiário, permitindo avaliar se a carga de trabalho está bem distribuída.

Monitoramento de Qualidade (Metas SMART): Alertas de pacientes com metas atrasadas há muito tempo ou estagnadas, permitindo intervenção pedagógica do professor.

Inteligência Epidemiológica: Gráficos mostrando o perfil da clínica (ex: 40% dos pacientes estão na Ortopedia, 60% são mulheres, patologias mais comuns via CID).

Gestão de Prontuários: Permissão para ler todos os prontuários de seus alunos supervisionados e, se necessário, fazer apontamentos.

Em sistemas de Prontuário Eletrônico, nós evitamos ao máximo (e muitas vezes é legalmente proibido) implementar rotas de exclusão total (DELETE físico) ou edição livre (PUT/PATCH em dados clínicos).

Vou te explicar como a regra de negócios funciona para cada um e te passar o código da edição de Pacientes (que realmente faltou eu te mandar!).

1. Por que NÃO deletar ou editar dados clínicos?
Evoluções e Medições (Imutáveis): O que o estagiário registrou no dia do atendimento é um documento legal. Se ele errou algo, na prática clínica, ele não "apaga" nem "edita" a evolução de ontem; ele cria uma nova evolução hoje fazendo uma "Retificação". Por isso, não teremos edição nem exclusão aqui.

Metas SMART: Uma vez traçada, a meta guia o tratamento. A edição do progresso dela já é feita automaticamente pelo sistema quando inserimos uma nova Medição.

Prontuários: Um prontuário nunca é deletado. Se o paciente recebe alta, nós apenas mudamos o status dele para "Alta" (algo que também podemos automatizar ou criar uma rota de encerramento depois).

2. Onde a Edição (PATCH) e a "Exclusão" fazem sentido?
Faz sentido para dados cadastrais (telefone que mudou, e-mail, etc.). Porém, em vez de deletar do banco (DELETE), nós fazemos o chamado Soft Delete: apenas mudamos a variável is_ativo para False. Assim, o paciente ou usuário some das telas de busca, mas o histórico dele continua preservado no banco para auditoria.