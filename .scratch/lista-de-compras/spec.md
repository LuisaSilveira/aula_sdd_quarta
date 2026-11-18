## Problem Statement

Uma pessoa que organiza suas compras no dispositivo precisa separar compras de ocasiões diferentes, registrar o que pretende comprar e acompanhar o que já foi comprado. Sem uma estrutura de listas persistentes, itens se misturam, compras recorrentes precisam ser reconstruídas manualmente e não há uma forma segura de consultar uma compra concluída sem perdê-la.

## Solution

Construir um aplicativo local de lista de compras com múltiplas listas nomeadas, persistidas em um arquivo JSON no dispositivo. Cada lista terá itens com nome obrigatório e dados opcionais de quantidade, unidade e preço unitário em reais. A pessoa poderá acompanhar itens comprados, consultar totais estimados, arquivar listas concluídas e restaurá-las quando precisar repetir uma compra.

O aplicativo terá uma interface HTML renderizada no servidor, simples, bonita e mobile-first. As regras de negócio ficarão separadas da interface e serão exercitadas diretamente pelo módulo de regras das listas, sem Flask nem HTTP.

## User Stories

1. As um usuário local, quero criar uma lista nomeada, para organizar uma ocasião ou objetivo de compra.
2. As um usuário local, quero ver todas as minhas listas ativas, para escolher rapidamente qual compra estou preparando.
3. As um usuário local, quero manter várias listas ao mesmo tempo, para não misturar compras semanais, churrascos e farmácia.
4. As um usuário local, quero renomear uma lista ativa, para corrigir ou atualizar seu propósito.
5. As um usuário local, quero excluir uma lista ativa com confirmação, para remover uma lista que não preciso mais sem apagá-la por acidente.
6. As um usuário local, quero criar uma lista vazia, para prepará-la antes de saber quais itens vou comprar.
7. As um usuário local, quero adicionar um item pelo nome, para registrar algo que preciso obter.
8. As um usuário local, quero editar o nome de um item, para corrigir erros ou tornar a descrição mais clara.
9. As um usuário local, quero informar a quantidade de um item, para registrar quanto pretendo comprar.
10. As um usuário local, quero usar quantidades decimais, para registrar compras por peso ou volume, como 1,5 kg.
11. As um usuário local, quero escolher uma unidade opcional, para distinguir unidades, peso, volume, pacotes, caixas ou dúzias.
12. As um usuário local, quero informar o preço unitário de um item, para acompanhar uma estimativa do custo.
13. As um usuário local, quero informar preço zero, para registrar itens gratuitos sem violar a validação.
14. As um usuário local, quero editar quantidade, unidade e preço de um item, para manter os dados da compra atualizados.
15. As um usuário local, quero adicionar dois itens com o mesmo nome, para preservar intenções distintas sem mesclagem automática.
16. As um usuário local, quero marcar um item como comprado, para distinguir o que já foi adquirido do que ainda está pendente.
17. As um usuário local, quero desmarcar um item comprado, para corrigir uma marcação ou indicar que preciso comprá-lo novamente.
18. As um usuário local, quero continuar vendo itens comprados na lista, para manter o contexto completo da compra.
19. As um usuário local, quero ocultar ou mostrar itens comprados, para reduzir a distração durante uma compra sem perder os dados.
20. As um usuário local, quero remover um item com confirmação, para limpar a lista sem perder um item por toque acidental.
21. As um usuário local, quero que a ordem de inclusão dos itens seja preservada, para manter uma sequência familiar durante a compra.
22. As um usuário local, quero ver o total estimado da lista, para ter uma noção do custo antes de finalizar a compra.
23. As um usuário local, quero que o total estimado considere quantidade 1 quando houver preço, mas não houver quantidade, para que um item unitário ainda contribua para a estimativa.
24. As um usuário local, quero que o aplicativo indique quando o total é apenas estimado, para não confundi-lo com o valor final pago.
25. As um usuário local, quero que dados insuficientes não sejam apresentados como um total completo, para evitar uma estimativa enganosa.
26. As um usuário local, quero arquivar manualmente uma lista concluída, para tirá-la das listas ativas sem perder seu conteúdo.
27. As um usuário local, quero receber um alerta antes de arquivar uma lista com itens pendentes, para não esconder uma compra incompleta por engano.
28. As um usuário local, quero consultar meu histórico de listas arquivadas, para recuperar compras anteriores.
29. As um usuário local, quero abrir uma lista arquivada para consulta, para lembrar quais itens e marcações ela tinha.
30. As um usuário local, quero restaurar uma lista arquivada, para repetir uma compra mantendo exatamente seus itens, preços e marcações.
31. As um usuário local, quero que uma lista arquivada seja somente para consulta até ser restaurada, para evitar alterar acidentalmente o histórico.
32. As um usuário local, quero excluir permanentemente uma lista arquivada com confirmação explícita, para remover dados que não desejo manter.
33. As um usuário local, quero que listas ativas apareçam da mais recente para a mais antiga, para encontrar primeiro a lista que comecei recentemente.
34. As um usuário local, quero que o histórico apareça da lista arquivada mais recentemente para a mais antiga, para recuperar compras recentes com menos esforço.
35. As um usuário local, quero receber orientação quando ainda não houver listas, para entender o próximo passo em vez de encontrar uma tela vazia.
36. As um usuário local, quero que listas com nomes ativos repetidos sejam rejeitadas, para identificar cada lista sem ambiguidade.
37. As um usuário local, quero que diferenças de maiúsculas, minúsculas e espaços nas pontas não criem nomes ativos aparentemente diferentes, para manter a navegação consistente.
38. As um usuário local, quero que uma lista ativa possa ter o mesmo nome de uma lista arquivada, para repetir uma compra recorrente sem conflito com o histórico.
39. As um usuário local, quero que nomes vazios ou compostos apenas por espaços sejam rejeitados, para que toda lista e item tenha uma identificação útil.
40. As um usuário local, quero que quantidades zero ou negativas sejam rejeitadas, para evitar dados sem significado de compra.
41. As um usuário local, quero que preços negativos sejam rejeitados, para evitar totais incorretos.
42. As um usuário local, quero que cada alteração seja salva imediatamente, para não perder meu trabalho ao fechar ou recarregar a página.
43. As um usuário local, quero receber uma confirmação visual breve após uma alteração persistida, para saber que minha ação foi registrada.
44. As um usuário local, quero receber uma mensagem explícita quando uma alteração não puder ser persistida, para não acreditar que uma operação foi concluída quando não foi.
45. As um usuário local, quero que uma falha de persistência preserve os dados anteriores, para que um erro de arquivo não corrompa minha lista.
46. As um usuário local, quero usar o aplicativo sem conta ou login, para organizar compras diretamente no dispositivo.
47. As pessoas que compartilham o dispositivo, quero que vejam as mesmas listas locais, para colaborar informalmente sem permissões ou contas separadas.
48. As um usuário local, quero usar reais brasileiros como única moeda, para interpretar preços sem conversão ou configuração adicional.

## Implementation Decisions

- O produto será implementado em Python com Flask, HTML renderizado no servidor por templates Jinja2, CSS próprio mobile-first e sem biblioteca de UI ou framework JavaScript.
- A entrada HTTP será responsável por interpretar requisições, chamar as regras do domínio, selecionar respostas e renderizar a interface; ela não conterá regras de negócio das listas.
- Um módulo separado representará e aplicará as regras de listas e itens. Esse módulo deverá ser utilizável e testável sem Flask, HTTP ou dependência da camada de templates.
- A persistência será feita exclusivamente em um arquivo JSON local dentro da aplicação. Não haverá banco de dados, autenticação ou sincronização entre dispositivos.
- O domínio terá listas ativas e listas arquivadas. Arquivar será uma ação manual e reversível por restauração; excluir uma lista arquivada será permanente.
- Listas arquivadas preservarão nome, itens, ordem, preços, quantidades, unidades e marcações de comprado. Enquanto arquivadas, serão somente leitura.
- Listas ativas terão nomes únicos após normalização de espaços nas pontas e diferenças de maiúsculas/minúsculas. Uma lista ativa poderá compartilhar nome com uma lista arquivada.
- Uma lista poderá estar vazia. Seu ciclo de vida não dependerá da quantidade de itens.
- Um item terá nome obrigatório e poderá ter quantidade positiva decimal, unidade opcional e preço unitário opcional em reais. Preço zero será válido; preço negativo não será.
- As unidades serão selecionadas de um conjunto curto e explícito, incluindo unidade, kg, g, litro, ml, pacote, caixa e dúzia. Não haverá conversão automática entre unidades.
- Itens com nomes iguais serão permitidos e não serão mesclados automaticamente.
- Itens serão mantidos na ordem de inclusão. Editar ou desmarcar um item não alterará sua posição.
- Marcar um item como comprado não o removerá da lista. Itens comprados ficarão visíveis por padrão e poderão ser ocultados por um controle de visualização.
- O total estimado será calculado somente a partir de itens com dados suficientes. Um item com preço e sem quantidade contribuirá como uma unidade para o cálculo, sem preencher quantidade automaticamente. O resultado será identificado como estimativa.
- Arquivar uma lista com itens pendentes exigirá confirmação. Não haverá arquivamento automático ao comprar o último item.
- A tela inicial separará listas ativas do histórico, mostrará resumo de pendentes/comprados e oferecerá a criação da primeira lista no estado vazio.
- Listas ativas serão ordenadas pela criação mais recente; listas arquivadas, pelo arquivamento mais recente.
- Criação, edição, marcação, remoção, arquivamento e restauração serão operações persistidas imediatamente, sem botão global de salvamento.
- Operações destrutivas exigirão confirmação explícita. Não haverá mecanismo de desfazer nesta versão.
- Falhas de leitura ou escrita serão expostas à interface com mensagem de erro apropriada. A interface não exibirá sucesso quando a persistência falhar, e a operação não substituirá os dados anteriores.

## Testing Decisions

- A única seam de teste será o módulo de regras das listas, no nível mais alto que permita validar o comportamento do domínio sem Flask nem HTTP.
- Os testes verificarão comportamento externo: estados observáveis das listas e itens, resultados de operações, validações, ordenação, cálculo de total, arquivamento/restauração e erros de persistência quando essa responsabilidade estiver exposta pelo módulo.
- Não serão testados detalhes internos de implementação, estrutura de classes, nomes privados, formato incidental do JSON ou renderização de templates.
- O módulo de regras será testado com cenários de criação, edição, exclusão, itens repetidos, marcação e desmarcação de comprado, preservação da ordem e listas vazias.
- Haverá casos de fronteira para nomes vazios, nomes ativos duplicados após normalização, quantidade decimal, quantidade zero/negativa, preço zero/negativo, unidade ausente, preço sem quantidade e totais com dados incompletos.
- Haverá casos de ciclo de vida para arquivamento manual com e sem pendências, confirmação de arquivamento, consulta somente leitura, restauração fiel e exclusão permanente do histórico.
- Haverá casos para garantir que cada operação válida possa ser persistida imediatamente e que uma falha de persistência não produza sucesso falso nem descarte o estado anterior.
- Como o repositório ainda não possui código ou testes de aplicação, não há prior art interno a reutilizar; os testes seguirão pytest e serão adicionados junto ao módulo de regras.

## Out of Scope

- Contas, login, permissões, perfis ou separação de dados por usuário.
- Compartilhamento ou sincronização entre dispositivos.
- Banco de dados, armazenamento remoto ou múltiplos arquivos de persistência.
- Preços por moeda diferente de reais brasileiros, conversão cambial ou histórico de variação de preços.
- Preços de marca, descontos, impostos, cupons, pagamento ou valor final da compra.
- Categorias, etiquetas, corredores, receitas, imagens ou informações nutricionais.
- Ordenação manual, agrupamento ou reordenação automática de itens.
- Mesclagem automática ou deduplicação de itens.
- Edição de listas arquivadas sem restauração.
- Lixeira, recuperação após exclusão permanente ou desfazer operações.
- Arquivamento automático baseado em itens comprados.
- Aplicativo nativo, framework JavaScript, biblioteca de UI ou API pública separada.

## Further Notes

- A linguagem da interface deve usar “lista”, “lista ativa”, “lista arquivada”, “histórico”, “item”, “item comprado”, “preço”, “total estimado” e “usuário local” conforme o glossário do projeto.
- O ciclo de vida de arquivamento e restauração está registrado na decisão arquitetural correspondente e deve ser preservado ao implementar a interface.
- Esta especificação descreve o primeiro corte funcional do produto; detalhes cosméticos podem evoluir sem alterar as regras do domínio.
