from flask import Flask, render_template

from .regras_listas import estado_inicial


def create_app():
    application = Flask(__name__)

    @application.get("/")
    def pagina_inicial():
        estado_inicial()
        return render_template("index.html")

    return application
