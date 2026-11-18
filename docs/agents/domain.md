# Domain Docs

Este repositorio usa layout single-context.

## Antes de explorar

- Leia `GLOSSARY.md` na raiz, se existir.
- Leia ADRs relevantes em `docs/adr/` para a area que sera modificada.
- Se os arquivos nao existirem, prossiga silenciosamente.
- O skill `/domain-modeling` cria esses documentos quando termos ou decisoes forem resolvidos.

## Estrutura

```text
/
├── GLOSSARY.md
├── docs/
│   └── adr/
└── app/
```

## Vocabulario

Ao nomear conceitos de dominio em issues, propostas, refactoracoes ou testes, use os termos definidos em `GLOSSARY.md`. Nao use sinonimos que o glossario explicitamente desaconselha.

## Conflitos com ADRs

Se uma proposta contradizer um ADR existente, informe o conflito explicitamente em vez de silenciosamente sobrescrever a decisao.
