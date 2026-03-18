## Checkpoint IA Generativa - Comparativo de Frameworks de Agentes

Este projeto foi desenvolvido para mostrar, de forma pratica, como diferentes frameworks resolvem problemas parecidos com arquiteturas diferentes.

Objetivo principal:

- Construir agentes funcionais
- Integrar com fontes de dados locais e externas
- Comparar estilo de orquestracao entre frameworks

## Visao humana do que foi feito

Ao inves de fazer tudo igual em todos os frameworks, a estrategia foi:

1. Consolidar uma base neurodevocional no LangChain
2. Evoluir para multiagente no CrewAI
3. Trocar de dominio no LangGraph para destacar grafo de estados
4. Trocar de dominio no LlamaIndex para destacar indexacao e sintese documental

Isso deixa a apresentacao mais madura, porque mostra decisao de arquitetura e nao apenas repeticao de codigo.

## Versao 1 - LangChain

Pasta: [langchain_version](langchain_version)

Tema: Neurodevocional AI

Por que usar LangChain aqui:

- Facilita criar agente com tools e memoria
- Permite controlar bem o fluxo de entrada e resposta
- Muito bom para um primeiro MVP com consistencia

Como funciona:

- Usuario faz check-in emocional
- Agente consulta base local (JSON biblico + neurociencia)
- Resposta e gerada em formato pratico para o dia

## Versao 2 - CrewAI

Pasta: [crewai_version](crewai_version)

Tema: Neurodevocional AI (mesmo dominio, orquestracao diferente)

Por que usar CrewAI:

- Destacar colaboracao entre papeis especializados
- Separar analise emocional e construcao de resposta final

Como funciona:

- Dois agentes: analista emocional e conselheiro neurodevocional
- Uso de dados locais
- Enriquecimento com APIs externas sem chave (ZenQuotes e Bible-API)

Diferenca percebida:

- Saida mais autoral e menos engessada
- Estrategia mais clara de "times de agentes"

## Versao 3 - LangGraph

Pasta: [langgraph_version](langgraph_version)

Tema: Planejamento de Viagens

Por que usar LangGraph:

- Mostrar pipeline por etapas com estado compartilhado
- Ideal para fluxos previsiveis e rastreaveis

Como funciona:

- Nos sequenciais: enriquecer destino -> clima -> atracoes -> custo -> relatorio final
- APIs externas sem chave: Open-Meteo e Wikipedia

Diferenca percebida:

- Clareza total do fluxo de execucao
- Facil de explicar visualmente na apresentacao

## Versao 4 - LlamaIndex

Pasta: [llamaindex_version](llamaindex_version)

Tema: Analise e Resumo de Noticias

Por que usar LlamaIndex:

- Foco em indexar e sintetizar documentos
- Excelente para transformar varias fontes em insight unico

Como funciona:

- Coleta noticias por tema (Hacker News Algolia API)
- Converte em documentos
- Cria indice de sumario
- Gera relatorio executivo com tendencias e recomendacoes

Diferenca percebida:

- Estrategia orientada a conhecimento indexado
- Muito forte para contexto documental

## Como manter tudo funcionando sem quebrar nada

Cada versao usa ambiente virtual proprio para evitar conflito de dependencias:

- LangChain: venv
- CrewAI: venv_crewai
- LangGraph: venv_langgraph
- LlamaIndex: venv_llamaindex

Essa foi uma decisao de engenharia importante para garantir estabilidade durante testes e apresentacao.

## Conclusao

O projeto nao so implementa agentes, mas demonstra criterio tecnico:

- Cada framework foi usado onde faz mais sentido
- O desenho das arquiteturas mudou conforme o problema
- Houve preocupacao com robustez, fallback e organizacao de ambiente

Esse conjunto mostra maturidade de projeto e vai alem de uma prova de conceito simples.
