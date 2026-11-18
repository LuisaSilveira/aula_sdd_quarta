def test_pagina_inicial_vazia(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True).strip() == ""
