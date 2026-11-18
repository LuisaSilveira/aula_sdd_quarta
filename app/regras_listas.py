import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


class NomeListaInvalido(ValueError):
    pass


class NomeListaDuplicado(ValueError):
    pass


class ListaNaoEncontrada(KeyError):
    pass


class ListaArquivadaNaoEncontrada(KeyError):
    pass


class ConfirmacaoArquivamentoPendente(ValueError):
    pass


class NomeItemInvalido(ValueError):
    pass


class ItemNaoEncontrado(KeyError):
    pass


class QuantidadeInvalida(ValueError):
    pass


class UnidadeInvalida(ValueError):
    pass


class PrecoInvalido(ValueError):
    pass


UNIDADES_PERMITIDAS = (
    "unidade",
    "kg",
    "g",
    "litro",
    "ml",
    "pacote",
    "caixa",
    "dúzia",
)


_NAO_INFORMADO = object()


def _converter_decimal(valor):
    if isinstance(valor, bool) or valor is None:
        raise InvalidOperation
    if isinstance(valor, str):
        valor = valor.strip().replace(",", ".")
        if not valor:
            raise InvalidOperation
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        raise InvalidOperation


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


def _buscar_lista_ativa(estado, lista_id):
    for lista in estado["listas_ativas"]:
        if lista["id"] == lista_id:
            lista.setdefault("itens", [])
            lista.setdefault("mostrar_itens_comprados", True)
            for item_existente in lista["itens"]:
                item_existente.setdefault("quantidade", None)
                item_existente.setdefault("unidade", None)
                item_existente.setdefault("preco_unitario", None)
            return lista
    raise ListaNaoEncontrada("Lista ativa não encontrada.")


def _buscar_item(lista, item_id):
    for item in lista["itens"]:
        if item["id"] == item_id:
            return item
    raise ItemNaoEncontrado("Item não encontrado.")


def validar_nome_item(nome):
    if not isinstance(nome, str) or not nome.strip():
        raise NomeItemInvalido("Nome do item é obrigatório.")
    return " ".join(nome.split())


def validar_quantidade(valor):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    try:
        quantidade = _converter_decimal(valor)
        if not quantidade.is_finite() or quantidade <= 0:
            raise QuantidadeInvalida("Quantidade deve ser maior que zero.")
    except (InvalidOperation, ValueError):
        raise QuantidadeInvalida("Quantidade deve ser maior que zero.")
    return float(quantidade)


def validar_unidade(unidade):
    if unidade is None or (isinstance(unidade, str) and not unidade.strip()):
        return None
    if not isinstance(unidade, str):
        raise UnidadeInvalida("Unidade não é válida.")
    unidade_limpa = unidade.strip()
    if unidade_limpa not in UNIDADES_PERMITIDAS:
        raise UnidadeInvalida("Unidade não é válida.")
    return unidade_limpa


def validar_preco_unitario(valor):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    try:
        preco = _converter_decimal(valor)
        if not preco.is_finite() or preco < 0:
            raise PrecoInvalido("Preço unitário não pode ser negativo.")
    except InvalidOperation:
        raise PrecoInvalido("Preço unitário não pode ser negativo.")
    return float(preco)


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
        "itens": [],
        "mostrar_itens_comprados": True,
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


def _buscar_lista_arquivada(estado, lista_id):
    for lista in estado["historico"]:
        lista.setdefault("itens", [])
        lista.setdefault("mostrar_itens_comprados", True)
        for item in lista["itens"]:
            item.setdefault("quantidade", None)
            item.setdefault("unidade", None)
            item.setdefault("preco_unitario", None)
        if lista["id"] == lista_id:
            return lista
    raise ListaArquivadaNaoEncontrada("Lista arquivada não encontrada.")


def arquivar_lista(
    estado,
    lista_id,
    confirmar_pendencias=False,
    arquivada_em=None,
):
    lista = _buscar_lista_ativa(estado, lista_id)
    tem_pendencias = any(not item.get("comprado", False) for item in lista["itens"])
    if tem_pendencias and not confirmar_pendencias:
        raise ConfirmacaoArquivamentoPendente(
            "A lista possui itens pendentes. Confirme o arquivamento."
        )

    copia = deepcopy(lista)
    copia["arquivada_em"] = arquivada_em or datetime.now(timezone.utc).isoformat()
    estado["historico"].append(copia)
    estado["listas_ativas"].remove(lista)
    return copia


def listar_historico(estado):
    return sorted(
        estado["historico"],
        key=lambda lista: lista.get("arquivada_em", ""),
        reverse=True,
    )


def buscar_lista_arquivada(estado, lista_id):
    return _buscar_lista_arquivada(estado, lista_id)


def restaurar_lista(estado, lista_id):
    arquivada = _buscar_lista_arquivada(estado, lista_id)
    nome_limpo = arquivada["nome"]
    if _nome_ja_existe(estado, nome_limpo):
        raise NomeListaDuplicado("Uma lista ativa já existe com esse nome.")

    restaurada = deepcopy(arquivada)
    restaurada.pop("arquivada_em", None)
    for indice, lista in enumerate(estado["historico"]):
        if lista["id"] == lista_id:
            estado["historico"].pop(indice)
            break
    estado["listas_ativas"].append(restaurada)
    return restaurada


def excluir_lista_arquivada(estado, lista_id, confirmar=False):
    if not confirmar:
        raise ValueError("confirmação explícita é necessária para excluir permanentemente.")
    for indice, lista in enumerate(estado["historico"]):
        if lista["id"] == lista_id:
            return estado["historico"].pop(indice)
    raise ListaArquivadaNaoEncontrada("Lista arquivada não encontrada.")


def adicionar_item(
    estado,
    lista_id,
    nome,
    quantidade=_NAO_INFORMADO,
    unidade=_NAO_INFORMADO,
    preco_unitario=_NAO_INFORMADO,
):
    lista = _buscar_lista_ativa(estado, lista_id)
    nome_limpo = validar_nome_item(nome)
    quantidade_limpa = (
        None
        if quantidade is _NAO_INFORMADO
        else validar_quantidade(quantidade)
    )
    unidade_limpa = (
        None
        if unidade is _NAO_INFORMADO
        else validar_unidade(unidade)
    )
    preco_limpo = (
        None
        if preco_unitario is _NAO_INFORMADO
        else validar_preco_unitario(preco_unitario)
    )
    item = {
        "id": str(uuid.uuid4()),
        "nome": nome_limpo,
        "comprado": False,
        "quantidade": quantidade_limpa,
        "unidade": unidade_limpa,
        "preco_unitario": preco_limpo,
    }
    lista["itens"].append(item)
    return item


def editar_item(
    estado,
    lista_id,
    item_id,
    nome,
    quantidade=_NAO_INFORMADO,
    unidade=_NAO_INFORMADO,
    preco_unitario=_NAO_INFORMADO,
):
    lista = _buscar_lista_ativa(estado, lista_id)
    item = _buscar_item(lista, item_id)
    nome_limpo = validar_nome_item(nome)

    quantidade_nova = (
        validar_quantidade(item.get("quantidade"))
        if quantidade is _NAO_INFORMADO
        else validar_quantidade(quantidade)
    )
    unidade_nova = (
        validar_unidade(item.get("unidade"))
        if unidade is _NAO_INFORMADO
        else validar_unidade(unidade)
    )
    preco_novo = (
        validar_preco_unitario(item.get("preco_unitario"))
        if preco_unitario is _NAO_INFORMADO
        else validar_preco_unitario(preco_unitario)
    )

    item["nome"] = nome_limpo
    item["quantidade"] = quantidade_nova
    item["unidade"] = unidade_nova
    item["preco_unitario"] = preco_novo
    return item


def marcar_item_comprado(estado, lista_id, item_id):
    lista = _buscar_lista_ativa(estado, lista_id)
    item = _buscar_item(lista, item_id)
    item["comprado"] = True
    return item


def desmarcar_item_comprado(estado, lista_id, item_id):
    lista = _buscar_lista_ativa(estado, lista_id)
    item = _buscar_item(lista, item_id)
    item["comprado"] = False
    return item


def ocultar_itens_comprados(estado, lista_id):
    lista = _buscar_lista_ativa(estado, lista_id)
    lista["mostrar_itens_comprados"] = False
    return lista


def mostrar_itens_comprados(estado, lista_id):
    lista = _buscar_lista_ativa(estado, lista_id)
    lista["mostrar_itens_comprados"] = True
    return lista


def remover_item(estado, lista_id, item_id):
    lista = _buscar_lista_ativa(estado, lista_id)
    for indice, item in enumerate(lista["itens"]):
        if item["id"] == item_id:
            return lista["itens"].pop(indice)
    raise ItemNaoEncontrado("Item não encontrado.")


def calcular_total_estimado(estado, lista_id=None):
    if lista_id is None:
        lista = estado
    elif isinstance(estado, dict):
        lista = next(
            (item for item in estado["listas_ativas"] if item["id"] == lista_id),
            None,
        )
        if lista is None:
            raise ListaNaoEncontrada("Lista ativa não encontrada.")
    else:
        raise ListaNaoEncontrada("Lista ativa não encontrada.")

    total = Decimal("0")
    for item in lista.get("itens", []):
        preco = item.get("preco_unitario")
        if preco is None:
            continue
        quantidade = item.get("quantidade")
        if quantidade is None:
            quantidade = Decimal("1")
        else:
            try:
                quantidade = _converter_decimal(quantidade)
            except InvalidOperation:
                continue
        try:
            preco_decimal = _converter_decimal(preco)
        except InvalidOperation:
            continue
        total += quantidade * preco_decimal
    return float(total)


def carregar_estado(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        return estado_inicial()
    with caminho.open("r", encoding="utf-8") as arquivo:
        estado = json.load(arquivo)
    estado.setdefault("listas_ativas", [])
    estado.setdefault("historico", [])
    for lista in estado["listas_ativas"]:
        lista.setdefault("itens", [])
        lista.setdefault("mostrar_itens_comprados", True)
        for item in lista["itens"]:
            item.setdefault("quantidade", None)
            item.setdefault("unidade", None)
            item.setdefault("preco_unitario", None)
    for lista in estado["historico"]:
        lista.setdefault("itens", [])
        lista.setdefault("mostrar_itens_comprados", True)
        for item in lista["itens"]:
            item.setdefault("quantidade", None)
            item.setdefault("unidade", None)
            item.setdefault("preco_unitario", None)
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

    def arquivar(
        self,
        lista_id,
        confirmar_pendencias=False,
        arquivada_em=None,
    ):
        return arquivar_lista(
            self.estado,
            lista_id,
            confirmar_pendencias=confirmar_pendencias,
            arquivada_em=arquivada_em,
        )

    def listar_historico(self):
        return listar_historico(self.estado)

    def buscar_arquivada(self, lista_id):
        return buscar_lista_arquivada(self.estado, lista_id)

    def restaurar(self, lista_id):
        return restaurar_lista(self.estado, lista_id)

    def excluir_arquivada(self, lista_id, confirmar=False):
        return excluir_lista_arquivada(
            self.estado,
            lista_id,
            confirmar=confirmar,
        )

    def adicionar_item(
        self,
        lista_id,
        nome,
        quantidade=_NAO_INFORMADO,
        unidade=_NAO_INFORMADO,
        preco_unitario=_NAO_INFORMADO,
    ):
        return adicionar_item(
            self.estado,
            lista_id,
            nome,
            quantidade=quantidade,
            unidade=unidade,
            preco_unitario=preco_unitario,
        )

    def editar_item(
        self,
        lista_id,
        item_id,
        nome,
        quantidade=_NAO_INFORMADO,
        unidade=_NAO_INFORMADO,
        preco_unitario=_NAO_INFORMADO,
    ):
        return editar_item(
            self.estado,
            lista_id,
            item_id,
            nome,
            quantidade=quantidade,
            unidade=unidade,
            preco_unitario=preco_unitario,
        )

    def marcar_comprado(self, lista_id, item_id):
        return marcar_item_comprado(self.estado, lista_id, item_id)

    def desmarcar_comprado(self, lista_id, item_id):
        return desmarcar_item_comprado(self.estado, lista_id, item_id)

    def ocultar_comprados(self, lista_id):
        return ocultar_itens_comprados(self.estado, lista_id)

    def mostrar_comprados(self, lista_id):
        return mostrar_itens_comprados(self.estado, lista_id)

    def remover_item(self, lista_id, item_id):
        return remover_item(self.estado, lista_id, item_id)

    def calcular_total_estimado(self, lista_id):
        return calcular_total_estimado(self.estado, lista_id)


# Nomes de conveniência para a API pública do domínio.
criar_lista_ativa = criar_lista
listar_listas = listar_listas_ativas
renomear_lista_ativa = renomear_lista
excluir_lista_ativa = excluir_lista
listar_listas_historico = listar_historico
arquivar_lista_ativa = arquivar_lista
buscar_lista_do_historico = buscar_lista_arquivada
restaurar_lista_arquivada = restaurar_lista
excluir_lista_do_historico = excluir_lista_arquivada
ler_estado = carregar_estado
persistir_estado = salvar_estado
total_estimado = calcular_total_estimado
