import json
from typing import List

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool

try:
	from . import tools as data_tools
	from .chains import build_agent_prompt, build_llm
except ImportError:
	import tools as data_tools
	from chains import build_agent_prompt, build_llm


class UserContextInput(BaseModel):
	como_me_sinto_hoje: str = Field(description="Como o usuario esta se sentindo hoje")
	como_acordei: str = Field(description="Como o usuario acordou")
	o_que_passou_ontem: str = Field(description="Resumo do que aconteceu ontem")
	atividades_de_hoje: str = Field(description="Atividades e responsabilidades de hoje")


class ThemeInput(BaseModel):
	theme: str = Field(description="Tema para consulta, como ansiedade, medo, cansaco, foco ou sabedoria")


def prepare_full_context_tool(
	como_me_sinto_hoje: str,
	como_acordei: str,
	o_que_passou_ontem: str,
	atividades_de_hoje: str,
) -> str:
	"""Prepare the full devotional context based on user check-in fields."""
	payload = data_tools.prepare_devotional_context(
		como_me_sinto_hoje=como_me_sinto_hoje,
		como_acordei=como_acordei,
		o_que_passou_ontem=o_que_passou_ontem,
		atividades_de_hoje=atividades_de_hoje,
	)
	return json.dumps(payload, ensure_ascii=False)


def get_bible_theme_data_tool(theme: str) -> str:
	"""Return biblical references and message for the requested theme."""
	return json.dumps(data_tools.get_bible_theme_data(theme), ensure_ascii=False)


def get_neuroscience_theme_data_tool(theme: str) -> str:
	"""Return neuroscience explanation and practical guidance for the requested theme."""
	return json.dumps(data_tools.get_neuroscience_theme_data(theme), ensure_ascii=False)


def build_tools() -> List[StructuredTool]:
	"""Create and return all tools available to the conversational agent."""
	return [
		StructuredTool.from_function(
			func=prepare_full_context_tool,
			name="prepare_full_context",
			description=(
				"Use para transformar os 4 campos do check-in emocional em contexto estruturado. "
				"Retorna tema detectado e bases biblica/neurocientifica."
			),
			args_schema=UserContextInput,
		),
		StructuredTool.from_function(
			func=get_bible_theme_data_tool,
			name="get_bible_theme_data",
			description="Busca dados biblicos de um tema especifico.",
			args_schema=ThemeInput,
		),
		StructuredTool.from_function(
			func=get_neuroscience_theme_data_tool,
			name="get_neuroscience_theme_data",
			description="Busca dados de neurociencia de um tema especifico.",
			args_schema=ThemeInput,
		),
	]


def create_agent_executor(verbose: bool = False) -> AgentExecutor:
	"""Create a conversation-ready agent executor with memory and tools."""
	tools = build_tools()
	llm = build_llm()
	prompt = build_agent_prompt()

	memory = ConversationBufferMemory(
		memory_key="chat_history",
		return_messages=True,
	)

	agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

	return AgentExecutor(
		agent=agent,
		tools=tools,
		memory=memory,
		verbose=verbose,
		max_iterations=6,
		handle_parsing_errors=True,
	)


def run_agent_turn(executor: AgentExecutor, user_input: str) -> str:
	"""Run one user turn through the agent and return assistant output."""
	result = executor.invoke({"input": user_input})
	return result.get("output", "Nao consegui gerar uma resposta agora.")
