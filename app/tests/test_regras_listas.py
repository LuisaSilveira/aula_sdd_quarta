import json

import pytest

from app.regras_listas import (
    ConfirmacaoArquivamentoPendente,
    ItemNaoEncontrado,
    ListaArquivadaNaoEncontrada,
    NomeListaDuplicado,
    NomeListaInvalido,
    NomeItemInvalido,
    QuantidadeInvalida,
    UnidadeInvalida,
    PrecoInvalido,
    adicionar_item,
    criar_lista,
    excluir_lista,
    estado_inicial,
    editar_item,
    listar_listas_ativas,
    calcular_total_estimado,
    carregar_estado,
    marcar_item_comprado,
    desmarcar_item_comprado,
    ocultar_itens_comprados,
    mostrar_itens_comprados,
    remover_item,
    renomear_lista,
    salvar_estado,
    arquivar_lista,
    listar_historico,
    buscar_lista_arquivada,
    restaurar_lista,
    excluir_lista_arquivada,
)


def test_ciclo_de_vida_arquivamento_consulta_restauracao_e_exclusao():
    estado = estado_inicial()
    lista = criar_lista(estado, "Feira", criada_em="2026-11-18T10:00:00Z")
    comprado = adicionar_item(estado, lista["id"], "Tomate")
    pendente = adicionar_item(estado, lista["id"], "Arroz")
    editar_item(
        estado,
        lista["id"],
        comprado["id"],
        "Tomate cereja",
        quantidade="1",
        unidade="kg",
        preco_unitario="8,50",
    )
    marcar_item_comprado(estado, lista["id"], comprado["id"])
    ocultar_itens_comprados(estado, lista["id"])

    estado_antes = json.loads(json.dumps(lista))
    arquivada = arquivar_lista(
        estado,
        lista["id"],
        confirmar_pendencias=True,
        arquivada_em="2026-11-18T12:00:00Z",
    )

    assert estado["listas_ativas"] == []
    assert arquivada["nome"] == "Feira"
    assert [item["nome"] for item in arquivada["itens"]] == [
        "Tomate cereja",
        "Arroz",
    ]
    assert arquivada["mostrar_itens_comprados"] is False
    assert [item["id"] for item in arquivada["itens"]] == [
        comprado["id"],
        pendente["id"],
    ]
    assert buscar_lista_arquivada(estado, lista["id"])["id"] == lista["id"]
    assert [item["id"] for item in listar_historico(estado)] == [lista["id"]]

    restaurada = restaurar_lista(estado, lista["id"])
    assert [item["id"] for item in restaurada["itens"]] == [
        comprado["id"],
        pendente["id"],
    ]
    assert restaurada["mostrar_itens_comprados"] is False
    assert estado["historico"] == []
    assert restaurada["nome"] == estado_antes["nome"]
    assert restaurada["itens"] == estado_antes["itens"]
    assert restaurada["criada_em"] == estado_antes["criada_em"]

    arquivar_lista(
        estado,
        lista["id"],
        confirmar_pendencias=True,
        arquivada_em="2026-11-18T13:00:00Z",
    )
    removida = excluir_lista_arquivada(estado, lista["id"], confirmar=True)
    assert removida["id"] == lista["id"]
    assert estado["historico"] == []


def test_arquivamento_pendente_exige_confirmacao_e_historico_e_por_recencia():
    estado = estado_inicial()
    antiga = criar_lista(estado, "Antiga", criada_em="2026-11-18T09:00:00Z")
    adicionar_item(estado, antiga["id"], "Pendente")

    with pytest.raises(ConfirmacaoArquivamentoPendente, match="pendente"):
        arquivar_lista(estado, antiga["id"])

    arquivar_lista(
        estado,
        antiga["id"],
        confirmar_pendencias=True,
        arquivada_em="2026-11-18T10:00:00Z",
    )
    nova = criar_lista(estado, "Nova")
    arquivar_lista(
        estado,
        nova["id"],
        arquivada_em="2026-11-18T11:00:00Z",
    )

    assert [item["id"] for item in listar_historico(estado)] == [
        nova["id"],
        antiga["id"],
    ]


def test_restaura_lista_nao_arquivada_e_exclusao_permanente_exigem_confirmacao():
    estado = estado_inicial()
    lista = criar_lista(estado, "Mercado")
    arquivar_lista(estado, lista["id"], arquivada_em="2026-11-18T12:00:00Z")

    with pytest.raises(ListaArquivadaNaoEncontrada):
        buscar_lista_arquivada(estado, "inexistente")
    with pytest.raises(ValueError, match="confirmação"):
        excluir_lista_arquivada(estado, lista["id"])
    with pytest.raises(ListaArquivadaNaoEncontrada):
        restaurar_lista(estado, "inexistente")


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


def test_quantidade_decimal_unidade_preco_e_edicao_do_item():
    estado = estado_inicial()
    lista = criar_lista(estado, "Churrasco")
    item = adicionar_item(estado, lista["id"], "Picanha")

    editar_item(
        estado,
        lista["id"],
        item["id"],
        "Picanha maturada",
        quantidade="1,5",
        unidade="kg",
        preco_unitario="49,90",
    )

    assert item["nome"] == "Picanha maturada"
    assert item["quantidade"] == 1.5
    assert item["unidade"] == "kg"
    assert item["preco_unitario"] == 49.90


@pytest.mark.parametrize("quantidade", ["0", "-1", "0,0", "-0,5"])
def test_quantidade_zero_ou_negativa_e_rejeitada(quantidade):
    estado = estado_inicial()
    lista = criar_lista(estado, "Mercado")
    item = adicionar_item(estado, lista["id"], "Arroz")

    with pytest.raises(QuantidadeInvalida, match="Quantidade"):
        editar_item(
            estado,
            lista["id"],
            item["id"],
            "Arroz",
            quantidade=quantidade,
        )


def test_unidade_opcional_e_preco_zero_valido_preco_negativo_invalido():
    estado = estado_inicial()
    lista = criar_lista(estado, "Mercado")
    item = adicionar_item(estado, lista["id"], "Brinde")

    editar_item(
        estado,
        lista["id"],
        item["id"],
        "Brinde",
        unidade="",
        preco_unitario="0",
    )
    assert item["unidade"] is None
    assert item["preco_unitario"] == 0

    with pytest.raises(UnidadeInvalida, match="Unidade"):
        editar_item(
            estado,
            lista["id"],
            item["id"],
            "Brinde",
            unidade="saco",
        )

    with pytest.raises(PrecoInvalido, match="Preço"):
        editar_item(
            estado,
            lista["id"],
            item["id"],
            "Brinde",
            preco_unitario="-0,01",
        )


def test_total_estimado_precos_sem_dados_suficientes_e_quantidade_implicita():
    estado = estado_inicial()
    lista = criar_lista(estado, "Semanal")
    arroz = adicionar_item(estado, lista["id"], "Arroz")
    leite = adicionar_item(estado, lista["id"], "Leite")
    cafe = adicionar_item(estado, lista["id"], "Café")

    editar_item(
        estado, lista["id"], arroz["id"], "Arroz",
        quantidade="2", preco_unitario="12,50",
    )
    editar_item(
        estado, lista["id"], leite["id"], "Leite",
        preco_unitario="4",
    )

    assert leite["quantidade"] is None
    assert calcular_total_estimado(estado, lista["id"]) == 29.0

    editar_item(
        estado, lista["id"], cafe["id"], "Café",
        quantidade="1",
    )
    assert calcular_total_estimado(estado, lista["id"]) == 29.0
