from typing import Optional

from langchain.agents import AgentExecutor

try:
	from .agent import create_agent_executor, run_agent_turn
	from . import tools as data_tools
except ImportError:
	from agent import create_agent_executor, run_agent_turn
	import tools as data_tools


def _is_quota_or_rate_limit_error(error: Exception) -> bool:
	"""Detect OpenAI quota/rate-limit failures by message content."""
	message = str(error).lower()
	markers = [
		"insufficient_quota",
		"rate limit",
		"ratelimit",
		"error code: 429",
	]
	return any(marker in message for marker in markers)


def _build_offline_response(
	como_me_sinto_hoje: str,
	como_acordei: str,
	o_que_passou_ontem: str,
	atividades_de_hoje: str,
	reason: str = "",
) -> str:
	"""Generate a local fallback response using only project JSON knowledge."""
	ctx = data_tools.prepare_devotional_context(
		como_me_sinto_hoje=como_me_sinto_hoje,
		como_acordei=como_acordei,
		o_que_passou_ontem=o_que_passou_ontem,
		atividades_de_hoje=atividades_de_hoje,
	)

	tema = ctx.get("detected_theme", "sabedoria")
	bible = ctx.get("bible_data", {})
	neuro = ctx.get("neuroscience_data", {})
	versiculos = bible.get("versiculos", []) if isinstance(bible, dict) else []
	v1 = versiculos[0] if versiculos else {}
	v2 = versiculos[1] if len(versiculos) > 1 else {}

	partes = [
		"Modo offline temporario (sem chamada ao modelo).",
		"",
		"1) Leitura emocional do momento",
		f"Seu relato aponta sinais ligados ao tema '{tema}'.",
		"",
		"2) Tema principal identificado",
		tema,
		"",
		"3) Base biblica",
	]

	if v1:
		partes.append(f"- {v1.get('referencia', '')}: {v1.get('texto', '')}")
	if v2:
		partes.append(f"- {v2.get('referencia', '')}: {v2.get('texto', '')}")
	if isinstance(bible, dict) and bible.get("mensagem"):
		partes.append(f"Aplicacao: {bible.get('mensagem')}")

	partes.extend(
		[
			"",
			"4) Apoio da neurociencia",
			neuro.get("explicacao", "Sem explicacao disponivel para este tema."),
			"",
			"5) Plano pratico para hoje (3 passos)",
		]
	)

	pratica = neuro.get("pratica", "Respire por 2 minutos, organize prioridades e faca pausas conscientes.")
	partes.extend(
		[
			f"- Passo 1: Ore por 2 minutos e entregue suas preocupacoes a Deus.",
			f"- Passo 2: Escolha 3 prioridades do dia e execute uma por vez.",
			f"- Passo 3: Aplique esta pratica: {pratica}",
			"",
			"Obs: A API OpenAI retornou quota insuficiente (429). Assim que regularizar billing/quota, o modo completo com agente volta automaticamente.",
		]
	)

	if reason:
		partes.append(f"Detalhe tecnico: {reason}")

	return "\n".join(partes)


def build_checkin_message(
	como_me_sinto_hoje: str,
	como_acordei: str,
	o_que_passou_ontem: str,
	atividades_de_hoje: str,
) -> str:
	"""Build a standardized user message for the neurodevotional check-in."""
	return (
		"Quero um direcionamento neurodevocional para hoje.\\n"
		f"- Como me sinto hoje: {como_me_sinto_hoje}\\n"
		f"- Como acordei: {como_acordei}\\n"
		f"- O que passou ontem: {o_que_passou_ontem}\\n"
		f"- Atividades de hoje: {atividades_de_hoje}\\n\\n"
		"Use as ferramentas para identificar tema, trazer base biblica e neurociencia, "
		"e me dar um plano pratico de 3 passos para melhorar meu dia."
	)


def get_or_create_executor(executor: Optional[AgentExecutor] = None) -> AgentExecutor:
	"""Return an existing executor or create a new one."""
	if executor is not None:
		return executor
	return create_agent_executor(verbose=False)


def process_checkin(
	executor: Optional[AgentExecutor],
	como_me_sinto_hoje: str,
	como_acordei: str,
	o_que_passou_ontem: str,
	atividades_de_hoje: str,
) -> tuple[AgentExecutor, str]:
	"""Process check-in fields and return executor + assistant response."""
	active_executor = get_or_create_executor(executor)
	user_message = build_checkin_message(
		como_me_sinto_hoje=como_me_sinto_hoje,
		como_acordei=como_acordei,
		o_que_passou_ontem=o_que_passou_ontem,
		atividades_de_hoje=atividades_de_hoje,
	)
	try:
		response = run_agent_turn(active_executor, user_message)
	except Exception as error:
		if _is_quota_or_rate_limit_error(error):
			response = _build_offline_response(
				como_me_sinto_hoje=como_me_sinto_hoje,
				como_acordei=como_acordei,
				o_que_passou_ontem=o_que_passou_ontem,
				atividades_de_hoje=atividades_de_hoje,
					reason=str(error),
			)
		else:
			raise
	return active_executor, response


def process_chat_message(
	executor: Optional[AgentExecutor],
	user_message: str,
) -> tuple[AgentExecutor, str]:
	"""Process one free-form user message and return executor + response."""
	active_executor = get_or_create_executor(executor)
	try:
		response = run_agent_turn(active_executor, user_message)
	except Exception as error:
		if _is_quota_or_rate_limit_error(error):
			response = (
				"A API retornou quota insuficiente (429). No modo de conversa livre, regularize billing/quota da OpenAI "
				"para continuar. Se preferir, use o tab 'Check-in guiado' para receber resposta offline baseada nos JSONs locais."
			)
		else:
			raise
	return active_executor, response


def reset_conversation() -> None:
	"""Reset conversation state; executor will be lazily created on next message."""
	return None
