from app.regras_listas import estado_inicial


def test_estado_inicial_nao_tem_listas():
    assert estado_inicial() == {
        "listas_ativas": [],
        "historico": [],
    }
