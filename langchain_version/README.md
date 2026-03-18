## Neurodevocional AI

Este projeto foi construído para gerar orientações diárias que unem espiritualidade cristã e neurociência de forma prática.

A proposta do produto é simples: a pessoa faz um check-in emocional e recebe uma resposta com acolhimento, direção bíblica e um plano de ação objetivo para o dia.

## O que foi feito na parte do LangChain

Na implementação em [langchain_version/streamlit_app.py](langchain_version/streamlit_app.py), o fluxo já está funcional e testado com:

- Interface de entrada (check-in guiado e conversa livre)
- Criação de agente com LangChain
- Ferramentas conectadas à base local em JSON
- Memória de conversa durante a sessão
- Fallback offline para quando a API da OpenAI estiver sem quota

Arquivos centrais dessa versão:

- [langchain_version/streamlit_app.py](langchain_version/streamlit_app.py): interface e estado da sessão
- [langchain_version/app.py](langchain_version/app.py): orquestração entre UI, agente e fallback
- [langchain_version/agent.py](langchain_version/agent.py): criação do agente, tools e memory
- [langchain_version/chains.py](langchain_version/chains.py): prompt do sistema e configuração do modelo
- [langchain_version/tools.py](langchain_version/tools.py): leitura dos JSONs e preparação de contexto

## Orquestramento (visão humana)

Em termos práticos, o que acontece é:

1. A pessoa conta como está se sentindo.
2. O app organiza essa entrada em um formato consistente.
3. O agente usa ferramentas para consultar a base local.
4. O modelo monta a resposta em 5 partes claras.
5. A conversa fica com memória para manter continuidade.

Fluxo técnico resumido:

1. Interface envia dados para [langchain_version/app.py](langchain_version/app.py).
2. [langchain_version/app.py](langchain_version/app.py) chama o executor do agente.
3. O executor é criado em [langchain_version/agent.py](langchain_version/agent.py) com `create_openai_functions_agent`.
4. As tools acessam os dados locais em [data/bible_topics.json](data/bible_topics.json) e [data/neuroscience_topics.json](data/neuroscience_topics.json).
5. O modelo gera uma saída final com leitura emocional, tema, base bíblica, neurociência e plano prático.

## Por que usar LangChain aqui

Escolhemos LangChain nesta etapa por três motivos principais:

- Facilita o uso de ferramentas com contrato claro de entrada e saída.
- Deixa a orquestração do agente mais explícita e modular.
- Permite evoluir para fluxos mais complexos sem reescrever toda a aplicação.

Isso combina bem com um produto que precisa de:

- Contexto conversacional
- Regras de resposta
- Integração entre raciocínio do modelo e base de dados local

## APIs e fontes usadas pelo agente

Hoje, o agente usa basicamente duas camadas de fonte:

- OpenAI API: para raciocínio e geração textual via `ChatOpenAI`.
- Base local de dados (JSON): para conteúdo bíblico e de neurociência via tools.

Ou seja, sua leitura está correta: não há integração com APIs externas de terceiros para conteúdo de domínio neste fluxo. O conteúdo temático vem da pasta [data/](data/).

## Estrutura de dados local

- [data/bible_topics.json](data/bible_topics.json): versículos e mensagens por tema
- [data/neuroscience_topics.json](data/neuroscience_topics.json): explicações e práticas por tema
- [data/devotional_examples.json](data/devotional_examples.json): exemplos de entradas e saídas

## Como executar

Na raiz do projeto:

```powershell
pip install -r requirements.txt
cd langchain_version
streamlit run streamlit_app.py
```

Variável obrigatória no arquivo `.env` da raiz:

```env
OPENAI_API_KEY=sua_chave
```

## Validação da primeira parte

Sim, a primeira parte da versão LangChain está válida para checkpoint funcional de agente:

- agente criado
- tools conectadas
- memória ativa
- interface funcionando
- fallback implementado

Como melhoria opcional, vale manter um ambiente virtual limpo para evitar avisos de dependência antiga que não afetam o fluxo atual.
