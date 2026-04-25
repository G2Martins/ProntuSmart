from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.database import get_database
from src.core.security import verify_password, create_access_token, get_password_hash, get_current_user
from src.models.dim_solicitacao import DimSolicitacaoCadastro, StatusSolicitacao
from src.models.dim_usuario import TipoPerfil
from src.schemas.auth import Token, TrocarSenhaRequest
from src.schemas.solicitacao import SolicitacaoCreate

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    # 1. Buscar usuário
    usuario = await db.dim_usuario.find_one({"matricula": form_data.username})
    if not usuario:
        raise HTTPException(status_code=400, detail="Matrícula ou senha incorretos.")
    
    # 2. Verificar se está ativo
    if not usuario.get("is_ativo", True):
        raise HTTPException(status_code=403, detail="Usuário inativo. Procure a administração.")

    # 3. Verificar senha
    if not verify_password(form_data.password, usuario["senha_hash"]):
        raise HTTPException(status_code=400, detail="Matrícula ou senha incorretos.")

    # 4. Criar o Token INJETANDO a flag de troca de senha
    access_token = create_access_token(
        data={
            "sub": str(usuario["_id"]),
            "perfil": usuario["perfil"],
            "nome": usuario["nome_completo"],
            "precisa_trocar_senha": usuario.get("precisa_trocar_senha", False) # <-- INJETADO NO JWT!
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- NOVA ROTA PARA EFETIVAR A TROCA ---
@router.post("/trocar-senha")
async def efetivar_troca_senha(
    dados: TrocarSenhaRequest, 
    current_user: dict = Depends(get_current_user), 
    db = Depends(get_database)
):
    # Verifica se a senha temporária digitada confere com a que está no banco (hash)
    if not verify_password(dados.senha_temporaria, current_user["senha_hash"]):
        raise HTTPException(status_code=400, detail="A senha provisória atual está incorreta.")
    
    # Encripta a nova senha digitada pelo usuário
    novo_hash = get_password_hash(dados.nova_senha)
    
    # Atualiza o banco e DESARMA a armadilha
    await db.dim_usuario.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "senha_hash": novo_hash, 
            "precisa_trocar_senha": False # 
        }}
    )
    
    return {"message": "Senha atualizada com sucesso!"}


@router.post("/registrar", status_code=status.HTTP_201_CREATED)
async def registrar_solicitacao(payload: SolicitacaoCreate, db = Depends(get_database)):
    """Cadastro público — cria solicitação pendente. Admin precisa aprovar."""
    # Bloqueia se já existe usuário com mesma matrícula/email
    if await db.dim_usuario.find_one({"matricula": payload.matricula}):
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada no sistema.")
    if await db.dim_usuario.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    # Bloqueia solicitações duplicadas pendentes
    pendente = await db.dim_solicitacao_cadastro.find_one({
        "$or": [
            {"matricula": payload.matricula},
            {"email":     payload.email},
        ],
        "status": StatusSolicitacao.PENDENTE,
    })
    if pendente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma solicitação pendente com esta matrícula ou e-mail.",
        )

    # Estagiário precisa de área
    if payload.perfil_solicitado == TipoPerfil.ESTAGIARIO and not payload.area_atendimento:
        raise HTTPException(
            status_code=400,
            detail="Estagiários devem informar a área de atendimento na solicitação.",
        )

    senha_hash = get_password_hash(payload.senha)
    solicitacao = DimSolicitacaoCadastro(
        nome_completo     = payload.nome_completo.strip(),
        matricula         = payload.matricula.strip(),
        email             = payload.email,
        senha_hash        = senha_hash,
        perfil_solicitado = payload.perfil_solicitado,
        area_atendimento  = payload.area_atendimento,
        justificativa     = payload.justificativa,
    )
    await db.dim_solicitacao_cadastro.insert_one(
        solicitacao.model_dump(by_alias=True, exclude_none=True)
    )
    return {
        "message": "Solicitação enviada! Você receberá acesso assim que o Administrador aprovar."
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna os dados do utilizador autenticado (sem senha_hash)."""
    return {
        "_id":           str(current_user["_id"]),
        "nome_completo": current_user["nome_completo"],
        "matricula":     current_user["matricula"],
        "email":         current_user["email"],
        "perfil":        current_user["perfil"],
        "is_ativo":      current_user.get("is_ativo", True),
        "criado_em":     current_user.get("criado_em"),
        "atualizado_em": current_user.get("atualizado_em"),
    }