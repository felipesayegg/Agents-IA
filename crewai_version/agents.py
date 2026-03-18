from crewai import Agent
from langchain_openai import ChatOpenAI

try:
	from .tools import get_crewai_tools
except ImportError:
	from tools import get_crewai_tools


def build_llm(model: str = "gpt-4o-mini", temperature: float = 0.4) -> ChatOpenAI:
	return ChatOpenAI(model=model, temperature=temperature)


def create_agents() -> dict[str, Agent]:
	llm = build_llm()
	tools = get_crewai_tools()

	emotional_analyst = Agent(
		role="Analista Emocional Cristao",
		goal=(
			"Entender o check-in do usuario com empatia, detectar o tema principal "
			"e sintetizar um diagnostico emocional sem julgamento."
		),
		backstory=(
			"Especialista em escuta ativa e leitura de contexto emocional. "
			"Seu foco e organizar os sinais do usuario para apoiar orientacao pratica."
		),
		llm=llm,
		tools=tools,
		verbose=False,
		allow_delegation=False,
	)

	neurodevotional_guide = Agent(
		role="Conselheiro Neurodevocional",
		goal=(
			"Gerar uma resposta organizada em 5 partes: leitura emocional, tema principal, "
			"base biblica, apoio da neurociencia e plano pratico de 3 passos."
		),
		backstory=(
			"Combina orientacao biblica com neurociencia aplicada para ajudar o usuario "
			"a viver o dia de forma mais consciente, confiante e funcional."
		),
		llm=llm,
		tools=tools,
		verbose=False,
		allow_delegation=False,
	)

	return {
		"emotional_analyst": emotional_analyst,
		"neurodevotional_guide": neurodevotional_guide,
	}
