# 04: Informar preços e mostrar total estimado

**What to build:** O usuário local consegue informar quantidade, unidade e preço unitário em reais para os itens e visualizar um total estimado honesto da lista, com validações para valores inválidos.

**Blocked by:** 03 — Adicionar e acompanhar itens comprados.

**Status:** done

- [x] Quantidades positivas, inclusive decimais, são aceitas.
- [x] Quantidade zero ou negativa é rejeitada com mensagem clara.
- [x] A unidade é opcional e usa opções compreensíveis, sem conversão automática.
- [x] Preço unitário em reais aceita zero e rejeita valores negativos.
- [x] O usuário consegue editar quantidade, unidade e preço de um item.
- [x] Um item com preço e sem quantidade contribui como uma unidade sem preencher o campo de quantidade.
- [x] O total estimado soma apenas dados suficientes e é identificado como estimativa.
- [x] Dados incompletos não são apresentados como total completo.
- [x] O cálculo e as validações são testados diretamente no módulo de regras das listas.
