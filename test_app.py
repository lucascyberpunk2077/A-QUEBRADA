import pytest
from app import app, init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def login(client, email, senha="123456"):
    return client.post(
        "/login",
        data={"email": email, "senha": senha},
        follow_redirects=True,
    )


# =========================================================
# TESTES POSITIVOS (FLUXOS ESPERADOS DO SISTEMA)
# =========================================================

def test_login_valido(client):
    resp = login(client, "u1@peladas.com", "123456")
    assert resp.status_code == 200
    assert b"A QUEBRADA" in resp.data


def test_cadastro_usuario_valido(client):
    resp = client.post(
        "/cadastro",
        data={
            "nome": "Jogador Pytest",
            "email": "pytest@peladas.com",
            "senha": "123456",
            "telefone": "5581988881111",
            "cidade": "Recife",
            "posicao_preferida": "Atacante",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Cadastro realizado com sucesso" in resp.data


def test_buscar_peladas_com_filtros(client):
    login(client, "u2@peladas.com")
    resp = client.get("/buscar?local=Boa+Viagem")
    assert resp.status_code == 200
    assert b"Ver detalhes" in resp.data


def test_crud_pelada_completo(client):
    login(client, "u1@peladas.com")

    # CREATE
    r_create = client.post(
        "/pelada/nova",
        data={
            "id_local": "1",
            "data": "2027-08-20",
            "hora": "20:00",
            "vagas_totais": "12",
            "valor_por_pessoa": "20",
            "nivel": "Intermediário",
            "descricao": "Pelada teste pytest",
        },
        follow_redirects=True,
    )
    assert r_create.status_code == 200

    # READ
    r_read = client.get("/minhas-peladas")
    assert b"2027-08-20 20:00" in r_read.data

    # UPDATE (id_pelada = 2)
    r_update = client.post(
        "/pelada/2/editar",
        data={
            "id_local": "1",
            "data": "2027-08-20",
            "hora": "21:00",
            "vagas_totais": "14",
            "valor_por_pessoa": "25",
            "nivel": "Competitivo",
            "descricao": "Pelada atualizada",
        },
        follow_redirects=True,
    )
    assert b"14 de 14" in r_update.data

    # DELETE
    r_delete = client.post("/pelada/2/excluir", follow_redirects=True)
    assert b"2027-08-20 21:00" not in r_delete.data


def test_solicitacao_aceite_e_whatsapp(client):
    login(client, "u2@peladas.com")
    client.post("/pelada/1/solicitar", data={"mensagem": "Bora jogar"}, follow_redirects=True)

    # Antes de aceitar, WhatsApp não é exibido
    r_antes = client.get("/pelada/1")
    assert b"wa.me/" not in r_antes.data

    # Organizador U1 aceita a solicitação 1
    login(client, "u1@peladas.com")
    client.post("/solicitacao/1/responder", data={"acao": "Aceita"}, follow_redirects=True)

    # Após aceitar, jogador U2 vê botão do WhatsApp
    login(client, "u2@peladas.com")
    r_depois = client.get("/pelada/1")
    assert b"wa.me/" in r_depois.data


def test_cancelar_propria_solicitacao(client):
    login(client, "u2@peladas.com")
    client.post("/pelada/1/solicitar", follow_redirects=True)

    resp = client.post("/solicitacao/1/cancelar", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Cancelada" in resp.data


def test_avaliacao_valida(client):
    login(client, "u2@peladas.com")
    client.post("/pelada/1/solicitar", follow_redirects=True)

    login(client, "u1@peladas.com")
    client.post("/solicitacao/1/responder", data={"acao": "Aceita"}, follow_redirects=True)

    login(client, "u2@peladas.com")
    r_ok = client.post(
        "/avaliar/1",
        data={"id_avaliado": "1", "nota": "5", "comentario": "Organizador nota 10"},
        follow_redirects=True,
    )
    assert "sucesso".encode("utf-8") in r_ok.data


# =========================================================
# TESTES NEGATIVOS (BLOQUEIOS, ERROS E REGRAS DE NEGÓCIO)
# =========================================================

def test_negativo_login_senha_incorreta_ou_campos_vazios(client):
    r_senha = login(client, "u1@peladas.com", "senha_errada")
    assert "inválidos".encode("utf-8") in r_senha.data

    r_vazio = login(client, "", "")
    assert "Preencha e-mail e senha".encode("utf-8") in r_vazio.data


def test_negativo_acesso_sem_autenticacao(client):
    for rota in ["/buscar", "/minhas-peladas", "/pelada/nova", "/solicitacoes", "/meus-pedidos"]:
        resp = client.get(rota, follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


def test_negativo_cadastro_email_duplicado(client):
    resp = client.post(
        "/cadastro",
        data={
            "nome": "Usuario Duplicado",
            "email": "u1@peladas.com",
            "senha": "123456",
        },
        follow_redirects=True,
    )
    assert "já está cadastrado".encode("utf-8") in resp.data


def test_negativo_criar_pelada_dados_invalidos(client):
    login(client, "u1@peladas.com")

    # Vagas iguais a zero
    r1 = client.post(
        "/pelada/nova",
        data={"id_local": "1", "data": "2027-08-20", "hora": "20:00", "vagas_totais": "0", "valor_por_pessoa": "15"},
    )
    assert b"maiores que zero" in r1.data

    # Valor por pessoa negativo
    r2 = client.post(
        "/pelada/nova",
        data={"id_local": "1", "data": "2027-08-20", "hora": "20:00", "vagas_totais": "10", "valor_por_pessoa": "-5"},
    )
    assert b"negativo" in r2.data

    # Data retroativa (no passado)
    r3 = client.post(
        "/pelada/nova",
        data={"id_local": "1", "data": "2020-01-01", "hora": "20:00", "vagas_totais": "10", "valor_por_pessoa": "15"},
    )
    assert "Data inválida".encode("utf-8") in r3.data


def test_negativo_editar_ou_excluir_pelada_de_outro_organizador(client):
    # U2 tenta editar ou excluir a pelada 1 (que pertence ao organizador U1)
    login(client, "u2@peladas.com")

    r_edit = client.get("/pelada/1/editar", follow_redirects=False)
    assert r_edit.status_code == 302
    assert "/minhas-peladas" in r_edit.headers["Location"]

    client.post("/pelada/1/excluir", follow_redirects=True)
    # Garante que a pelada 1 continua existindo
    r_check = client.get("/pelada/1")
    assert r_check.status_code == 200


def test_negativo_solicitacao_duplicada_ou_organizador_na_propria_pelada(client):
    # Organizador U1 tenta solicitar vaga na própria pelada 1
    login(client, "u1@peladas.com")
    r_org = client.post("/pelada/1/solicitar", follow_redirects=True)
    assert "própria pelada".encode("utf-8") in r_org.data

    # Jogador U2 solicita duas vezes na mesma pelada
    login(client, "u2@peladas.com")
    client.post("/pelada/1/solicitar", follow_redirects=True)
    r_dup = client.post("/pelada/1/solicitar", follow_redirects=True)
    assert "já possui uma solicitação".encode("utf-8") in r_dup.data


def test_negativo_avaliacao_a_si_mesmo_ou_nota_invalida(client):
    login(client, "u2@peladas.com")
    client.post("/pelada/1/solicitar", follow_redirects=True)

    login(client, "u1@peladas.com")
    client.post("/solicitacao/1/responder", data={"acao": "Aceita"}, follow_redirects=True)

    login(client, "u2@peladas.com")

    # Autoavaliação bloqueada
    r_auto = client.post(
        "/avaliar/1",
        data={"id_avaliado": "2", "nota": "5", "comentario": "Eu mesmo"},
        follow_redirects=True,
    )
    assert b"a si mesmo" in r_auto.data

    # Nota fora do intervalo 1..5
    r_nota = client.post(
        "/avaliar/1",
        data={"id_avaliado": "1", "nota": "10", "comentario": "Nota invalida"},
        follow_redirects=True,
    )
    assert b"entre 1 e 5" in r_nota.data