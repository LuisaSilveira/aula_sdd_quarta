# 02: Criar e gerenciar listas ativas

**What to build:** O usuário local consegue criar, consultar, renomear e excluir listas ativas pela interface, com persistência no arquivo JSON e nomes ativos obrigatórios e únicos após normalização de espaços e maiúsculas/minúsculas.

**Blocked by:** 01 — Criar esqueleto Flask e pytest.

**Status:** done

- [x] A tela inicial mostra as listas ativas ordenadas da mais recente para a mais antiga.
- [x] O usuário consegue criar uma lista com nome válido e vê a nova lista na interface.
- [x] Nomes vazios ou compostos apenas por espaços são rejeitados com mensagem clara.
- [x] Uma segunda lista ativa não pode repetir um nome já existente após normalização.
- [x] O usuário consegue renomear uma lista respeitando as mesmas validações de criação.
- [x] O usuário consegue excluir uma lista ativa após confirmação explícita.
- [x] Listas vazias são válidas e todas as operações persistem no JSON.
- [x] As regras de listas são exercitadas por testes sem Flask nem HTTP.
