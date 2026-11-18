# 06: Fechar estados vazios e falhas de persistência

**What to build:** A experiência completa orienta o primeiro uso, confirma salvamentos imediatos e informa falhas de persistência sem falso sucesso ou perda do estado anterior, mantendo ativas e histórico claros durante o uso em telas pequenas.

**Blocked by:** 04 — Informar preços e mostrar total estimado; 05 — Arquivar e restaurar listas pelo histórico.

**Status:** done

- [x] Quando não houver listas ativas, a tela inicial explica o próximo passo e oferece criar a primeira lista.
- [x] Listas ativas e histórico aparecem em áreas distintas e com ordenação por recência.
- [x] Cada alteração válida exibe confirmação visual breve após ser persistida.
- [x] Uma falha de leitura ou escrita informa explicitamente que a alteração não foi persistida.
- [x] Falha de persistência não exibe confirmação de sucesso nem substitui o estado anterior.
- [x] Os controles de itens comprados, confirmação de exclusão e confirmação de arquivamento permanecem claros em layout mobile-first.
- [x] Os cenários de erro e estados vazios são cobertos no nível do módulo de regras, sem testes dependentes de Flask ou HTTP.

