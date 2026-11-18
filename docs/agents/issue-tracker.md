# Issue tracker: Local Markdown

Issues e specs deste repositorio ficam como arquivos markdown locais em `.scratch/`.

## Convencoes

- Uma feature por diretorio: `.scratch/<feature-slug>/`
- A spec fica em `.scratch/<feature-slug>/spec.md`
- Issues de implementacao ficam em `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numeradas a partir de `01`
- O estado de uma issue fica registrado em uma linha `Status:` perto do topo
- Comentarios e historico da conversa sao adicionados ao final do arquivo, em uma secao `## Comments`

## Criar ou publicar

Ao publicar no tracker, crie um arquivo novo em `.scratch/<feature-slug>/issues/` e crie o diretorio, se necessario.

## Buscar uma issue

Leia o arquivo no caminho informado pelo usuario. O usuario normalmente passa o caminho ou o numero da issue diretamente.

## Fechar uma issue

Ao concluir uma issue:

- marque todos os criterios de aceite atendidos com `[x]`
- troque a linha `Status` para `Status: done`

## Operacoes do Wayfinder

- Map: `.scratch/<effort>/map.md`
- Issue filha: `.scratch/<effort>/issues/NN-<slug>.md`
- A linha `Type:` registra o tipo (`research`/`prototype`/`grilling`/`task`)
- A linha `Status:` registra `claimed`/`resolved`
- A linha `Blocked by: NN, NN` registra dependencias
- A issue pode ser resolvida quando todas as dependencias indicadas tiverem `Status: resolved`
