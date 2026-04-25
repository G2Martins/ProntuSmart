from src.schemas.paciente import PacienteCreate, PacienteUpdate


def paciente_payload(**overrides):
    payload = {
        "nome_completo": "Jose Eduardo Ferreira",
        "cpf": "065.675.891-08",
        "data_nascimento": "2004-06-28",
        "sexo": "Masculino",
        "telefone_contato": "(61) 98212-1759",
        "area_atendimento_atual": "Neurologia Adulto",
    }
    payload.update(overrides)
    return payload


def test_paciente_create_accepts_blank_optional_email():
    paciente = PacienteCreate.model_validate(paciente_payload(email=""))

    assert paciente.email is None


def test_paciente_update_accepts_blank_optional_email():
    paciente = PacienteUpdate.model_validate({"email": "   "})

    assert paciente.email is None


def test_paciente_create_keeps_valid_email_trimmed():
    paciente = PacienteCreate.model_validate(
        paciente_payload(email=" paciente@email.com ")
    )

    assert paciente.email == "paciente@email.com"
