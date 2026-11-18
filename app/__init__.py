from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from .regras_listas import (
    ListaNaoEncontrada,
    NomeListaDuplicado,
    NomeListaInvalido,
    carregar_estado,
    criar_lista,
    excluir_lista,
    listar_listas_ativas,
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

    return application
