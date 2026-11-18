import json

import pytest

from app.regras_listas import (
    NomeListaDuplicado,
    NomeListaInvalido,
    criar_lista,
    excluir_lista,
    estado_inicial,
    listar_listas_ativas,
    carregar_estado,
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
