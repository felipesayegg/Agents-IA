## LangGraph Version - Travel Planner AI

Tema escolhido para diferenciar do LangChain/CrewAI: **Agente de Planejamento de Viagens**.

Escolhi esse tema porque permite demonstrar bem o modelo de grafo com etapas claras e tambem integrar **APIs externas sem chave**.

## APIs externas usadas (sem chave)

- Open-Meteo Geocoding: localiza destino (cidade, pais, latitude/longitude)
- Open-Meteo Forecast: clima para os proximos dias
- Wikipedia OpenSearch: ideias de pontos de interesse

Todas sao chamadas `GET` publicas. Se alguma falhar, o fluxo usa fallback para nao quebrar a demonstracao.

## Orquestracao em grafo

Nos do LangGraph:

1. `enrich_destination`
2. `weather_forecast`
3. `attractions`
4. `cost_estimator`
5. `planner_writer`

Ordem de execucao: sequencial no grafo, encerrando em `END`.

Arquivos principais:

- [langgraph_version/state.py](langgraph_version/state.py)
- [langgraph_version/nodes.py](langgraph_version/nodes.py)
- [langgraph_version/graph.py](langgraph_version/graph.py)
- [langgraph_version/app.py](langgraph_version/app.py)
- [langgraph_version/streamlit_app.py](langgraph_version/streamlit_app.py)

## Como rodar sem afetar LangChain e CrewAI

Use um ambiente virtual dedicado ao LangGraph:

```powershell
cd neurodevocional-ai
python -m venv venv_langgraph
.\venv_langgraph\Scripts\Activate.ps1
pip install -r langgraph_version\requirements.txt
cd langgraph_version
streamlit run streamlit_app.py --server.port 8503
```

Abra: `http://localhost:8503`

## Comparacao rapida de proposta

- LangChain: fluxo de agente com tools no tema neurodevocional
- CrewAI: multiagente + enriquecimento externo no tema neurodevocional
- LangGraph: pipeline em grafo no tema viagens com APIs externas abertas

Assim, voce mostra variedade de arquitetura e de dominio no checkpoint.
