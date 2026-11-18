def test_pagina_inicial_vazia(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Nenhuma lista ativa" in response.get_data(as_text=True)


def test_criar_listar_renomear_e_excluir_por_interface(client):
    criada = client.post(
        "/listas",
        data={"nome": "Mercado"},
        follow_redirects=True,
    )
    assert criada.status_code == 200
    pagina = criada.get_data(as_text=True)
    assert "Mercado" in pagina

    from app.regras_listas import carregar_estado

    estado = carregar_estado(client.application.config["LISTAS_JSON"])
    lista_id = estado["listas_ativas"][0]["id"]

    renomeada = client.post(
        f"/listas/{lista_id}/renomear",
        data={"nome": "Mercado semanal"},
        follow_redirects=True,
    )
    assert "Mercado semanal" in renomeada.get_data(as_text=True)

    excluida = client.post(
        f"/listas/{lista_id}/excluir",
        data={"confirmar": "sim"},
        follow_redirects=True,
    )
    assert excluida.status_code == 200
    assert "Nenhuma lista ativa" in excluida.get_data(as_text=True)


def test_validacoes_da_interface(client):
    vazia = client.post("/listas", data={"nome": "  "}, follow_redirects=True)
    assert "Nome da lista é obrigatório" in vazia.get_data(as_text=True)

    client.post("/listas", data={"nome": "Casa"}, follow_redirects=True)
    duplicada = client.post(
        "/listas",
        data={"nome": " casa "},
        follow_redirects=True,
    )
    assert "já existe" in duplicada.get_data(as_text=True)
