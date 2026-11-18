from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from .regras_listas import (
    ItemNaoEncontrado,
    ListaNaoEncontrada,
    NomeListaDuplicado,
    NomeListaInvalido,
    NomeItemInvalido,
    adicionar_item,
    carregar_estado,
    criar_lista,
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

    def carregar():
        return carregar_estado(caminho_json)

    def persistir(estado):
        salvar_estado(caminho_json, estado)

    @application.get("/")
    def pagina_inicial():
        estado = carregar()
        return render_template(
            "index.html",
            listas=listar_listas_ativas(estado),
        )

    @application.post("/listas")
    @application.post("/criar-lista")
    def criar():
        estado = carregar()
        try:
            criar_lista(estado, request.form.get("nome", ""))
            persistir(estado)
            flash("Lista criada.")
        except (NomeListaInvalido, NomeListaDuplicado, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/renomear")
    @application.post("/renomear/<lista_id>")
    def renomear(lista_id):
        estado = carregar()
        try:
            renomear_lista(estado, lista_id, request.form.get("nome", ""))
            persistir(estado)
            flash("Lista renomeada.")
        except (ListaNaoEncontrada, NomeListaInvalido, NomeListaDuplicado, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/excluir")
    @application.post("/excluir/<lista_id>")
    def excluir(lista_id):
        if request.form.get("confirmar") != "sim":
            flash("Confirmação explícita é necessária para excluir a lista.")
            return redirect(url_for("pagina_inicial"))

        estado = carregar()
        try:
            excluir_lista(estado, lista_id)
            persistir(estado)
            flash("Lista excluída.")
        except (ListaNaoEncontrada, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens")
    def adicionar(lista_id):
        estado = carregar()
        try:
            adicionar_item(estado, lista_id, request.form.get("nome", ""))
            persistir(estado)
            flash("Item adicionado.")
        except (ListaNaoEncontrada, NomeItemInvalido, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/editar")
    def editar_item_interface(lista_id, item_id):
        estado = carregar()
        try:
            editar_item(estado, lista_id, item_id, request.form.get("nome", ""))
            persistir(estado)
            flash("Item editado.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, NomeItemInvalido, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/comprado")
    def marcar_comprado(lista_id, item_id):
        estado = carregar()
        try:
            marcar_item_comprado(estado, lista_id, item_id)
            persistir(estado)
            flash("Item marcado como comprado.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/pendente")
    def desmarcar_comprado(lista_id, item_id):
        estado = carregar()
        try:
            desmarcar_item_comprado(estado, lista_id, item_id)
            persistir(estado)
            flash("Item desmarcado como comprado.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/comprados/ocultar")
    def ocultar_comprados(lista_id):
        estado = carregar()
        try:
            ocultar_itens_comprados(estado, lista_id)
            persistir(estado)
            flash("Itens comprados ocultados.")
        except (ListaNaoEncontrada, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/comprados/mostrar")
    def mostrar_comprados(lista_id):
        estado = carregar()
        try:
            mostrar_itens_comprados(estado, lista_id)
            persistir(estado)
            flash("Itens comprados mostrados.")
        except (ListaNaoEncontrada, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    @application.post("/listas/<lista_id>/itens/<item_id>/remover")
    def remover(lista_id, item_id):
        if request.form.get("confirmar") != "sim":
            flash("Confirmação explícita é necessária para remover o item.")
            return redirect(url_for("pagina_inicial"))

        estado = carregar()
        try:
            remover_item(estado, lista_id, item_id)
            persistir(estado)
            flash("Item removido.")
        except (ListaNaoEncontrada, ItemNaoEncontrado, OSError) as erro:
            flash(str(erro))
        return redirect(url_for("pagina_inicial"))

    return application
