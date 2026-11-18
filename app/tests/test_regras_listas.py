import json

import pytest

from app.regras_listas import (
    ItemNaoEncontrado,
    NomeListaDuplicado,
    NomeListaInvalido,
    NomeItemInvalido,
    adicionar_item,
    criar_lista,
    excluir_lista,
    estado_inicial,
    editar_item,
    listar_listas_ativas,
    carregar_estado,
    marcar_item_comprado,
    desmarcar_item_comprado,
    ocultar_itens_comprados,
    mostrar_itens_comprados,
    remover_item,
    renomear_lista,
    salvar_estado,
)


def test_estado_inicial_nao_tem_listas():
    assert estado_inicial() == {
        "listas_ativas": [],
        "historico": [],
    }


def test_criar_lista_normalizada_e_exposta_da_mais_recente():
    estado = estado_inicial()
    primeira = criar_lista(estado, "  Mercado  ", criada_em="2026-11-18T10:00:00Z")
    segunda = criar_lista(estado, "Farmácia", criada_em="2026-11-18T11:00:00Z")

    assert primeira["nome"] == "Mercado"
    assert segunda["nome"] == "Farmácia"
    assert [lista["nome"] for lista in listar_listas_ativas(estado)] == [
        "Farmácia",
        "Mercado",
    ]


def test_nome_vazio_e_nome_duplicado_sao_rejeitados():
    estado = estado_inicial()
    criar_lista(estado, "Churrasco")

    with pytest.raises(NomeListaInvalido, match="Nome da lista"):
        criar_lista(estado, "   ")

    with pytest.raises(NomeListaDuplicado, match="já existe"):
        criar_lista(estado, "  churrasco ")


def test_renomear_e_excluir_listas():
    estado = estado_inicial()
    lista = criar_lista(estado, "Semanal")
    renomeada = renomear_lista(estado, lista["id"], " Mercado semanal ")

    assert renomeada["nome"] == "Mercado semanal"
    excluir_lista(estado, lista["id"])
    assert estado["listas_ativas"] == []


def test_renomear_valida_duplicidade_e_permite_nome_proprio():
    estado = estado_inicial()
    lista = criar_lista(estado, "Casa")
    criar_lista(estado, "Festa")

    renomear_lista(estado, lista["id"], " casa ")
    with pytest.raises(NomeListaDuplicado):
        renomear_lista(estado, lista["id"], "FESTA")


def test_persistencia_json_preserva_estado(tmp_path):
    caminho = tmp_path / "listas.json"
    estado = estado_inicial()
    criar_lista(estado, "Lista vazia")

    salvar_estado(caminho, estado)

    assert json.loads(caminho.read_text(encoding="utf-8"))["listas_ativas"]
    assert carregar_estado(caminho) == estado


def test_adicionar_editar_marcar_desmarcar_itens_e_preservar_ordem():
    estado = estado_inicial()
    lista = criar_lista(estado, "Feira")

    primeiro = adicionar_item(estado, lista["id"], "  Tomate ")
    repetido = adicionar_item(estado, lista["id"], "Tomate")

    assert primeiro["nome"] == "Tomate"
    assert primeiro["comprado"] is False
    assert repetido["nome"] == "Tomate"
    assert len(lista["itens"]) == 2

    editar_item(estado, lista["id"], primeiro["id"], " Tomate cereja ")
    marcar_item_comprado(estado, lista["id"], primeiro["id"])

    assert lista["itens"][0]["nome"] == "Tomate cereja"
    assert lista["itens"][0]["comprado"] is True
    assert [item["id"] for item in lista["itens"]] == [primeiro["id"], repetido["id"]]

    desmarcar_item_comprado(estado, lista["id"], primeiro["id"])
    assert lista["itens"][0]["comprado"] is False
    assert [item["id"] for item in lista["itens"]] == [primeiro["id"], repetido["id"]]


def test_nome_item_vazio_e_lista_inexistente_sao_rejeitados():
    estado = estado_inicial()
    lista = criar_lista(estado, "Mercado")

    with pytest.raises(NomeItemInvalido, match="Nome do item"):
        adicionar_item(estado, lista["id"], "  ")

    with pytest.raises(NomeItemInvalido):
        editar_item(estado, lista["id"], adicionar_item(estado, lista["id"], "Leite")["id"], "")

    with pytest.raises(ItemNaoEncontrado):
        editar_item(estado, lista["id"], "item-inexistente", "Leite")


def test_ocultar_mostrar_remover_e_persistir_itens(tmp_path):
    caminho = tmp_path / "estado-teste.json"
    estado = estado_inicial()
    lista = criar_lista(estado, "Casa")
    item = adicionar_item(estado, lista["id"], "Pão")

    ocultar_itens_comprados(estado, lista["id"])
    assert lista["mostrar_itens_comprados"] is False
    mostrar_itens_comprados(estado, lista["id"])
    assert lista["mostrar_itens_comprados"] is True

    removido = remover_item(estado, lista["id"], item["id"])
    assert removido["nome"] == "Pão"
    assert lista["itens"] == []

    with pytest.raises(ItemNaoEncontrado):
        remover_item(estado, lista["id"], item["id"])

    salvar_estado(caminho, estado)
    assert carregar_estado(caminho) == estado
