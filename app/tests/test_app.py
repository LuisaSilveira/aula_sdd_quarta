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


def test_adicionar_editar_marcar_ocultar_e_remover_itens_por_interface(client):
    client.post("/listas", data={"nome": "Feira"}, follow_redirects=True)
    from app.regras_listas import carregar_estado

    caminho = client.application.config["LISTAS_JSON"]
    estado = carregar_estado(caminho)
    lista_id = estado["listas_ativas"][0]["id"]

    client.post(
        f"/listas/{lista_id}/itens",
        data={"nome": "Tomate"},
        follow_redirects=True,
    )
    client.post(
        f"/listas/{lista_id}/itens",
        data={"nome": "Tomate"},
        follow_redirects=True,
    )
    estado = carregar_estado(caminho)
    primeiro = estado["listas_ativas"][0]["itens"][0]
    assert len(estado["listas_ativas"][0]["itens"]) == 2

    vazia = client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/editar",
        data={"nome": "  "},
        follow_redirects=True,
    )
    assert "Nome do item é obrigatório" in vazia.get_data(as_text=True)

    editada = client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/editar",
        data={"nome": "Tomate cereja"},
        follow_redirects=True,
    )
    assert "Tomate cereja" in editada.get_data(as_text=True)

    marcada = client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/comprado",
        follow_redirects=True,
    )
    pagina = marcada.get_data(as_text=True)
    assert "comprado" in pagina.lower()

    desmarcada = client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/pendente",
        follow_redirects=True,
    )
    assert "desmarcado" in desmarcada.get_data(as_text=True).lower()
    client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/comprado",
        follow_redirects=True,
    )

    ocultada = client.post(
        f"/listas/{lista_id}/comprados/ocultar",
        follow_redirects=True,
    )
    assert "Tomate cereja" not in ocultada.get_data(as_text=True)

    mostrada = client.post(
        f"/listas/{lista_id}/comprados/mostrar",
        follow_redirects=True,
    )
    assert "Tomate cereja" in mostrada.get_data(as_text=True)

    sem_confirmacao = client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/remover",
        follow_redirects=True,
    )
    assert "Tomate cereja" in sem_confirmacao.get_data(as_text=True)

    removida = client.post(
        f"/listas/{lista_id}/itens/{primeiro['id']}/remover",
        data={"confirmar": "sim"},
        follow_redirects=True,
    )
    assert "Tomate cereja" not in removida.get_data(as_text=True)
