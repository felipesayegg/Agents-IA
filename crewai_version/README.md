## CrewAI Version - Neurodevocional AI

Esta versao aplica o mesmo produto neurodevocional usando orquestracao com CrewAI.

A ideia e manter o mesmo tema (emocao + base biblica + neurociencia), porque isso deixa o checkpoint coerente entre frameworks e facilita comparar resultados entre LangChain, CrewAI, LangGraph e LlamaIndex.

## Arquitetura

- [crewai_version/core/context_builder.py](crewai_version/core/context_builder.py): leitura dos JSONs e deteccao de tema
- [crewai_version/tools.py](crewai_version/tools.py): wrappers de contexto e dados para uso no fluxo
- [crewai_version/agents.py](crewai_version/agents.py): definicao dos agentes
- [crewai_version/tasks.py](crewai_version/tasks.py): tarefas encadeadas
- [crewai_version/app.py](crewai_version/app.py): orquestracao do crew e fallback offline
- [crewai_version/streamlit_app.py](crewai_version/streamlit_app.py): interface web

## Agentes definidos

1. Analista Emocional Cristao
- interpreta o check-in
- identifica tema principal
- estrutura sinais e riscos do dia

2. Conselheiro Neurodevocional
- gera resposta final em 5 partes:
	- leitura emocional
	- tema principal
	- base biblica
	- apoio da neurociencia
	- plano pratico de 3 passos

## Fontes e APIs usadas

- OpenAI API: geracao e raciocinio do modelo
- Dados locais da pasta [data](data):
	- [data/bible_topics.json](data/bible_topics.json)
	- [data/neuroscience_topics.json](data/neuroscience_topics.json)
- API externa sem chave (GET):
	- ZenQuotes (`https://zenquotes.io/api/random`) para frase dinamica
	- Bible-API (`https://bible-api.com/<referencia>`) para versiculo dinamico por tema

As APIs externas entram como enriquecimento da resposta. Se falharem, o sistema usa fallback local.

## Como rodar sem afetar LangChain

Recomendado: usar um venv separado para o CrewAI.

```powershell
cd neurodevocional-ai
python -m venv venv_crewai
.\venv_crewai\Scripts\Activate.ps1
pip install -r crewai_version\requirements.txt
cd crewai_version
streamlit run streamlit_app.py --server.port 8502
```

Para rodar LangChain ao mesmo tempo, em outro terminal:

```powershell
cd neurodevocional-ai
.\venv\Scripts\Activate.ps1
cd langchain_version
streamlit run streamlit_app.py --server.port 8501
```

No arquivo `.env` da raiz:

```env
OPENAI_API_KEY=sua_chave
```

## Observacao

Se houver erro de quota/rate limit da OpenAI, o app responde em modo offline com base nos JSONs locais para voce nao perder a demonstracao.
