import json
from pathlib import Path
from copy import deepcopy

from flask import Flask, flash, redirect, render_template, request, url_for

from .regras_listas import (
    ConfirmacaoArquivamentoPendente,
    ItemNaoEncontrado,
    ListaArquivadaNaoEncontrada,
    ListaNaoEncontrada,
    NomeListaDuplicado,
    NomeListaInvalido,
    NomeItemInvalido,
    QuantidadeInvalida,
    UnidadeInvalida,
    PrecoInvalido,
    FalhaLeituraPersistencia,
    FalhaEscritaPersistencia,
    UNIDADES_PERMITIDAS,
    adicionar_item,
    carregar_estado,
    criar_lista,
    calcular_total_estimado,
    desmarcar_item_comprado,
    editar_item,
    excluir_lista,
    listar_listas_ativas,
    marcar_item_comprado,
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


def create_app(config=None):
    application = Flask(__name__)
    application.config["SECRET_KEY"] = "lista-de-compras-local"
    application.config["LISTAS_JSON"] = str(
        Path(application.root_path).parent / "listas.json"
    )
    if config:
        application.config.update(config)
    caminho_json = application.config["LISTAS_JSON"]
    ultimo_estado = {"valor": None}
    erro_leitura = {"valor": False}

    @application.template_filter("real")
    def formatar_real(valor):
        if valor is None:
            return ""
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def carregar():
        try:
            estado = carregar_estado(caminho_json)
            ultimo_estado["valor"] = deepcopy(estado)
            erro_leitura["valor"] = False
            return deepcopy(estado)
        except (FalhaLeituraPersistencia, OSError, json.JSONDecodeError) as erro:
            flash(str(erro), "erro")
            erro_leitura["valor"] = True
            if ultimo_estado["valor"] is None:
                return {"listas_ativas": [], "historico": []}
            return deepcopy(ultimo_estado["valor"])

    def persistir(estado):
        salvar_estado(caminho_json, estado)
        ultimo_estado["valor"] = deepcopy(estado)

    def sucesso(mensagem):
        flash(mensagem, "sucesso")

    def mensagem_erro(mensagem):
        flash(str(mensagem), "erro")

    @application.get("/")
    def pagina_inicial():
        estado = carregar()
        totais = {
            lista["id"]: calcular_total_estimado(estado, lista["id"])
            for lista in estado["listas_ativas"]
        }
        pendencias = {
            lista["id"]: sum(
                1 for item in lista["itens"] if not item.get("comprado", False)
            )
            for lista in estado["listas_ativas"]
        }
        return render_template(
            "index.html",
            listas=listar_listas_ativas(estado),
            historico=listar_historico(estado),
            totais=totais,
            pendencias=pendencias,
            unidades=UNIDADES_PERMITIDAS,
            erro_leitura=erro_leitura["valor"],
        )

    @application.get("/historico/<lista_id>")
    def consultar_historico(lista_id):
        estado = carregar()
        try:
            lista = buscar_lista_arquivada(estado, lista_id)
            total = calcular_total_estimado(lista)
            return render_template(
                "historico.html",
                lista=lista,
                total=total,
            )
        except ListaArquivadaNaoEncontrada as erro:
            mensagem_erro(str(erro))
            return redirect(url_for("pagina_inicial"))

    @application.post("/listas")
    @application.post("/criar-lista")
    def criar():
        estado = carregar()
        try:
            criar_lista(estado, request.form.get("nome", ""))
            persistir(estado)
            sucesso("Lista criada.")
        except (NomeListaInvalido, NomeListaDuplicado, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/renomear")
    @application.post("/renomear/<lista_id>")
    def renomear(lista_id):
        estado = carregar()
        try:
            renomear_lista(estado, lista_id, request.form.get("nome", ""))
            persistir(estado)
            sucesso("Lista renomeada.")
        except (ListaNaoEncontrada, NomeListaInvalido, NomeListaDuplicado, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/excluir")
    @application.post("/excluir/<lista_id>")
    def excluir(lista_id):
        if request.form.get("confirmar") != "sim":
            mensagem_erro("Confirmação explícita é necessária para excluir a lista.")
            return redirect(url_for("pagina_inicial"))

        estado = carregar()
        try:
            excluir_lista(estado, lista_id)
            persistir(estado)
            sucesso("Lista excluída.")
        except (ListaNaoEncontrada, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/arquivar")
    def arquivar(lista_id):
        estado = carregar()
        try:
            confirmar = request.form.get("confirmar_pendencias") == "sim"
            arquivar_lista(
                estado,
                lista_id,
                confirmar_pendencias=confirmar,
            )
            persistir(estado)
            sucesso("Lista arquivada.")
        except (
            ListaNaoEncontrada,
            ConfirmacaoArquivamentoPendente,
            OSError,
        ) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/historico/<lista_id>/restaurar")
    def restaurar(lista_id):
        estado = carregar()
        try:
            restaurar_lista(estado, lista_id)
            persistir(estado)
            sucesso("Lista restaurada.")
        except (
            ListaArquivadaNaoEncontrada,
            NomeListaDuplicado,
            OSError,
        ) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/historico/<lista_id>/excluir")
    def excluir_arquivada(lista_id):
        if request.form.get("confirmar") != "sim":
            mensagem_erro("confirmação explícita é necessária para excluir permanentemente.")
            return redirect(url_for("pagina_inicial"))
        estado = carregar()
        try:
            excluir_lista_arquivada(estado, lista_id, confirmar=True)
            persistir(estado)
            sucesso("Lista arquivada excluída permanentemente.")
        except (ListaArquivadaNaoEncontrada, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens")
    def adicionar(lista_id):
        estado = carregar()
        try:
            adicionar_item(
                estado,
                lista_id,
                request.form.get("nome", ""),
                quantidade=request.form.get("quantidade", ""),
                unidade=request.form.get("unidade", ""),
                preco_unitario=request.form.get("preco_unitario", ""),
            )
            persistir(estado)
            sucesso("Item adicionado.")
        except (
            ListaNaoEncontrada,
            NomeItemInvalido,
            QuantidadeInvalida,
            UnidadeInvalida,
            PrecoInvalido,
            OSError,
        ) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/editar")
    def editar_item_interface(lista_id, item_id):
        estado = carregar()
        try:
            argumentos = {}
            if "quantidade" in request.form:
                argumentos["quantidade"] = request.form.get("quantidade", "")
            if "unidade" in request.form:
                argumentos["unidade"] = request.form.get("unidade", "")
            if "preco_unitario" in request.form:
                argumentos["preco_unitario"] = request.form.get("preco_unitario", "")
            editar_item(
                estado,
                lista_id,
                item_id,
                request.form.get("nome", ""),
                **argumentos,
            )
            persistir(estado)
            sucesso("Item editado.")
        except (
            ListaNaoEncontrada,
            ItemNaoEncontrado,
            NomeItemInvalido,
            QuantidadeInvalida,
            UnidadeInvalida,
            PrecoInvalido,
            OSError,
        ) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/comprado")
    def marcar_comprado(lista_id, item_id):
        estado = carregar()
        try:
            marcar_item_comprado(estado, lista_id, item_id)
            persistir(estado)
            sucesso("Item marcado como comprado.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/pendente")
    def desmarcar_comprado(lista_id, item_id):
        estado = carregar()
        try:
            desmarcar_item_comprado(estado, lista_id, item_id)
            persistir(estado)
            sucesso("Item desmarcado como comprado.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/comprados/ocultar")
    def ocultar_comprados(lista_id):
        estado = carregar()
        try:
            ocultar_itens_comprados(estado, lista_id)
            persistir(estado)
            sucesso("Itens comprados ocultados.")
        except (ListaNaoEncontrada, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/comprados/mostrar")
    def mostrar_comprados(lista_id):
        estado = carregar()
        try:
            mostrar_itens_comprados(estado, lista_id)
            persistir(estado)
            sucesso("Itens comprados mostrados.")
        except (ListaNaoEncontrada, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/remover")
    def remover(lista_id, item_id):
        if request.form.get("confirmar") != "sim":
            mensagem_erro("Confirmação explícita é necessária para remover o item.")
            return redirect(url_for("pagina_inicial"))

        estado = carregar()
        try:
            remover_item(estado, lista_id, item_id)
            persistir(estado)
            sucesso("Item removido.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, OSError) as erro:
            mensagem_erro(str(erro))
        return redirect(url_for("pagina_inicial"))

    return application
