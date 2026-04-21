from fastapi import HTTPException


def normalizar_configuracao_limites(dados: dict, base: dict | None = None) -> dict:
    dados_normalizados = dict(dados)
    configuracao_atual = {
        "sem_limitacao_valor": True,
        "limite_minimo": None,
        "limite_maximo": None,
    }

    if base:
        configuracao_atual.update({
            "sem_limitacao_valor": base.get("sem_limitacao_valor", True),
            "limite_minimo": base.get("limite_minimo"),
            "limite_maximo": base.get("limite_maximo"),
        })

    configuracao_atual.update({
        "sem_limitacao_valor": dados_normalizados.get(
            "sem_limitacao_valor",
            configuracao_atual["sem_limitacao_valor"],
        ),
        "limite_minimo": dados_normalizados.get(
            "limite_minimo",
            configuracao_atual["limite_minimo"],
        ),
        "limite_maximo": dados_normalizados.get(
            "limite_maximo",
            configuracao_atual["limite_maximo"],
        ),
    })

    if (
        ("limite_minimo" in dados_normalizados or "limite_maximo" in dados_normalizados)
        and "sem_limitacao_valor" not in dados_normalizados
    ):
        configuracao_atual["sem_limitacao_valor"] = False

    if configuracao_atual["sem_limitacao_valor"]:
        dados_normalizados["sem_limitacao_valor"] = True
        dados_normalizados["limite_minimo"] = None
        dados_normalizados["limite_maximo"] = None
        return dados_normalizados

    limite_minimo = configuracao_atual["limite_minimo"]
    limite_maximo = configuracao_atual["limite_maximo"]

    if limite_minimo is None and limite_maximo is None:
        raise HTTPException(
            status_code=400,
            detail="Informe pelo menos um limite de valor ou marque a opção sem limitação.",
        )

    if (
        limite_minimo is not None and
        limite_maximo is not None and
        limite_minimo > limite_maximo
    ):
        raise HTTPException(
            status_code=400,
            detail="O limite mínimo não pode ser maior que o limite máximo.",
        )

    dados_normalizados["sem_limitacao_valor"] = False
    dados_normalizados["limite_minimo"] = limite_minimo
    dados_normalizados["limite_maximo"] = limite_maximo
    return dados_normalizados


def validar_valor_indicador(indicador: dict, valor: float, campo: str) -> None:
    if indicador.get("sem_limitacao_valor", True):
        return

    limite_minimo = indicador.get("limite_minimo")
    limite_maximo = indicador.get("limite_maximo")
    nome_indicador = indicador.get("nome", "Indicador")

    if limite_minimo is not None and valor < limite_minimo:
        raise HTTPException(
            status_code=400,
            detail=f'{campo} do indicador "{nome_indicador}" deve ser maior ou igual a {limite_minimo}.',
        )

    if limite_maximo is not None and valor > limite_maximo:
        raise HTTPException(
            status_code=400,
            detail=f'{campo} do indicador "{nome_indicador}" deve ser menor ou igual a {limite_maximo}.',
        )


def converter_valor_numerico(valor: object, campo: str) -> float:
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail=f"{campo} deve ser um valor numérico válido.",
        )
