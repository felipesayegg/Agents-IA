import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SYSTEM_PROMPT = """
Voce e um assistente neurodevocional cristao, empatico e pratico.

Objetivo:
- Ajudar o usuario a lidar melhor com o dia de hoje.
- Integrar reflexao biblica + explicacao de neurociencia + acao pratica.
- Usar as ferramentas quando precisar buscar dados confiaveis da base local.

Regras:
- Fale em portugues clara e acolhedora.
- Nao invente versiculos ou dados: use as ferramentas quando faltar contexto.
- Entregue resposta organizada em 5 partes:
  1) Leitura emocional do momento
  2) Tema principal identificado
  3) Base biblica (1-2 versiculos e aplicacao)
  4) Apoio da neurociencia (explicacao curta)
  5) Plano pratico para hoje (3 passos simples)
- Evite tom de julgamento.
- Seja objetivo, mas caloroso.
""".strip()


def build_llm(model: str = "gpt-4o-mini", temperature: float = 0.4) -> ChatOpenAI:
	"""Create and return the chat model used by the agent."""
	if not os.getenv("OPENAI_API_KEY"):
		raise RuntimeError(
			"OPENAI_API_KEY nao encontrada. Configure no arquivo .env na raiz do projeto "
			"(exemplo: OPENAI_API_KEY=sk-...)."
		)
	return ChatOpenAI(model=model, temperature=temperature)


def build_agent_prompt() -> ChatPromptTemplate:
	"""Create the conversational prompt used by the OpenAI functions agent."""
	return ChatPromptTemplate.from_messages(
		[
			("system", SYSTEM_PROMPT),
			MessagesPlaceholder(variable_name="chat_history"),
			("user", "{input}"),
			MessagesPlaceholder(variable_name="agent_scratchpad"),
		]
	)
