## LlamaIndex Version - Agente de Analise e Resumo de Noticias

Nesta versao, o foco foi usar LlamaIndex para um fluxo de analise de noticias com base em fontes externas sem chave.

Tema escolhido: Analise e resumo de noticias, seguindo a proposta sugerida no trabalho.

## O que esta implementado

- Coleta de noticias recentes via API publica do Hacker News Algolia
- Estruturacao dos dados em documentos para o LlamaIndex
- Criacao de indice de sumario para sintetizar tendencias
- Geracao de relatorio executivo em portugues
- Modo offline com resumo simples se a chave OpenAI nao estiver disponivel

Arquivos principais:

- [llamaindex_version/index_builder.py](llamaindex_version/index_builder.py)
- [llamaindex_version/query_engine.py](llamaindex_version/query_engine.py)
- [llamaindex_version/app.py](llamaindex_version/app.py)
- [llamaindex_version/streamlit_app.py](llamaindex_version/streamlit_app.py)

## APIs externas usadas

- Hacker News Algolia API (GET sem chave): noticias de tecnologia e inovacao
- GDELT DOC API (GET sem chave): cobertura mais ampla de noticias globais

Endpoints base:

- https://hn.algolia.com/api/v1/search_by_date
- https://api.gdeltproject.org/api/v2/doc/doc

## Como rodar sem afetar LangChain, CrewAI e LangGraph

Use um ambiente virtual dedicado:

1. cd neurodevocional-ai
2. python -m venv venv_llamaindex
3. .\venv_llamaindex\Scripts\Activate.ps1
4. pip install -r llamaindex_version\requirements.txt
5. cd llamaindex_version
6. streamlit run streamlit_app.py --server.port 8504

URL local:

- http://localhost:8504

## Diferencial desta abordagem

No LlamaIndex, o centro do fluxo e o indice e a sintese sobre documentos coletados.
Ou seja, a logica principal e recuperar e resumir contexto documental, ao inves de depender de um pipeline de tools ou de um grafo de etapas.
