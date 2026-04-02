BackEnd/
├── src/
│   ├── main.py                        ← Entry point FastAPI + CORS + lifespan
│   ├── api/
│   │   └── v1/
│   │       ├── router.py              ← Registra todas as rotas em /api/v1
│   │       └── routes/
│   │           ├── auth.py            ← POST /auth/login | /auth/register
│   │           ├── pacientes.py       ← CRUD /pacientes
│   │           ├── prontuarios.py     ← /prontuarios
│   │           ├── metas_smart.py     ← /metas-smart
│   │           ├── evolucoes.py       ← /evolucoes
│   │           └── medicoes.py        ← /medicoes
│   ├── core/
│   │   ├── config.py                  ← Settings via pydantic-settings + .env
│   │   ├── database.py                ← Motor async + índices automáticos
│   │   └── security.py                ← JWT, hash senha, get_current_user
│   ├── models/
│   │   ├── base.py                    ← MongoBaseModel + PyObjectId (Pydantic v2)
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
│   │   ├── auth_service.py            ← Login + criar usuário
│   │   ├── paciente_service.py        ← CRUD pacientes
│   │   ├── prontuario_service.py      ← Abrir prontuário + contador sessões
│   │   ├── meta_smart_service.py      ← Criar metas SMART + prazo automático
│   │   ├── evolucao_service.py        ← Inserir sessão + atualiza desnorm.
│   │   └── medicao_service.py         ← Registrar medição + calcular progresso
│   └── utils/
│       ├── helpers.py                 ← calcular_progresso, gerar_numero, serialize_doc
│       └── seed.py                    ← Popula dims iniciais + docente padrão
├── tests/
│   └── test_auth.py
├── .env                               ← Sua connection string MongoDB
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt