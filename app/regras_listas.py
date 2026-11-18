import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


class NomeListaInvalido(ValueError):
    pass


class NomeListaDuplicado(ValueError):
    pass


class ListaNaoEncontrada(KeyError):
    pass


def estado_inicial():
    """Retorna o estado inicial observável das listas."""
    return {
        "listas_ativas": [],
        "historico": [],
    }


def normalizar_nome(nome):
    if not isinstance(nome, str):
        return ""
    return " ".join(nome.strip().split()).casefold()


def validar_nome_lista(nome):
    if not isinstance(nome, str) or not nome.strip():
        raise NomeListaInvalido("Nome da lista é obrigatório.")
    return " ".join(nome.split())


def _nome_ja_existe(estado, nome, ignorar_id=None):
    chave = normalizar_nome(nome)
    return any(
        lista["id"] != ignorar_id
        and normalizar_nome(lista.get("nome", "")) == chave
        for lista in estado["listas_ativas"]
    )


def listar_listas_ativas(estado):
    return sorted(
        estado["listas_ativas"],
        key=lambda lista: lista.get("criada_em", ""),
        reverse=True,
    )


def criar_lista(estado, nome, criada_em=None):
    nome_limpo = validar_nome_lista(nome)
    if _nome_ja_existe(estado, nome_limpo):
        raise NomeListaDuplicado("Uma lista ativa já existe com esse nome.")

    lista = {
        "id": str(uuid.uuid4()),
        "nome": nome_limpo,
        "criada_em": criada_em or datetime.now(timezone.utc).isoformat(),
    }
    estado.setdefault("listas_ativas", []).append(lista)
    return lista


def renomear_lista(estado, lista_id, nome):
    lista = next(
        (item for item in estado["listas_ativas"] if item["id"] == lista_id),
        None,
    )
    if lista is None:
        raise ListaNaoEncontrada("Lista ativa não encontrada.")

    nome_limpo = validar_nome_lista(nome)
    if _nome_ja_existe(estado, nome_limpo, ignorar_id=lista_id):
        raise NomeListaDuplicado("Uma lista ativa já existe com esse nome.")

    lista["nome"] = nome_limpo
    return lista


def excluir_lista(estado, lista_id):
    for indice, lista in enumerate(estado["listas_ativas"]):
        if lista["id"] == lista_id:
            return estado["listas_ativas"].pop(indice)
    raise ListaNaoEncontrada("Lista ativa não encontrada.")


def carregar_estado(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        return estado_inicial()
    with caminho.open("r", encoding="utf-8") as arquivo:
        estado = json.load(arquivo)
    estado.setdefault("listas_ativas", [])
    estado.setdefault("historico", [])
    return estado


def salvar_estado(caminho, estado):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")
    with temporario.open("w", encoding="utf-8") as arquivo:
        json.dump(deepcopy(estado), arquivo, ensure_ascii=False, indent=2)
        arquivo.flush()
        os.fsync(arquivo.fileno())
    os.replace(temporario, caminho)


class GerenciadorListas:
    """API pública simples das regras das listas."""

    def __init__(self, estado=None):
        self.estado = estado if estado is not None else estado_inicial()

    def listar_ativas(self):
        return listar_listas_ativas(self.estado)

    def criar(self, nome, criada_em=None):
        return criar_lista(self.estado, nome, criada_em=criada_em)

    def renomear(self, lista_id, nome):
        return renomear_lista(self.estado, lista_id, nome)

    def excluir(self, lista_id):
        return excluir_lista(self.estado, lista_id)


# Nomes de conveniência para a API pública do domínio.
criar_lista_ativa = criar_lista
listar_listas = listar_listas_ativas
renomear_lista_ativa = renomear_lista
excluir_lista_ativa = excluir_lista
ler_estado = carregar_estado
persistir_estado = salvar_estado
