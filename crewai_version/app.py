import os
from pathlib import Path

from crewai import Crew, Process
from dotenv import load_dotenv

try:
	from .agents import create_agents
	from .tasks import create_tasks
	from .tools import compose_external_signals, prepare_full_context
except ImportError:
	from agents import create_agents
	from tasks import create_tasks
	from tools import compose_external_signals, prepare_full_context


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _is_quota_or_rate_limit_error(error: Exception) -> bool:
	message = str(error).lower()
	markers = ["insufficient_quota", "rate limit", "ratelimit", "error code: 429"]
	return any(marker in message for marker in markers)


def _build_offline_response(context_payload: dict, reason: str = "") -> str:
	tema = context_payload.get("detected_theme", "sabedoria")
	bible = context_payload.get("bible_data", {})
	neuro = context_payload.get("neuroscience_data", {})
	external = context_payload.get("external_signals", {})
	quote = external.get("quote", {}) if isinstance(external, dict) else {}
	verse = external.get("verse", {}) if isinstance(external, dict) else {}
	versiculos = bible.get("versiculos", []) if isinstance(bible, dict) else []
	v1 = versiculos[0] if versiculos else {}
	v2 = versiculos[1] if len(versiculos) > 1 else {}

	parts = [
		"Modo offline temporario (sem chamada ao modelo).",
		"",
		"Raio-X do seu momento",
		f"Seu relato aponta sinais ligados ao tema '{tema}'.",
		"",
		"Conexao biblica viva",
	]

	if v1:
		parts.append(f"- {v1.get('referencia', '')}: {v1.get('texto', '')}")
	if v2:
		parts.append(f"- {v2.get('referencia', '')}: {v2.get('texto', '')}")
	if isinstance(bible, dict) and bible.get("mensagem"):
		parts.append(f"Aplicacao: {bible.get('mensagem')}")

	if verse:
		parts.append(f"- API externa {verse.get('reference', '')}: {verse.get('text', '')}")

	parts.extend(
		[
			"",
			"Neuroacao tatica",
			neuro.get("explicacao", "Sem explicacao disponivel para este tema."),
			"",
			"Plano em 3 movimentos",
		]
	)
	pratica = neuro.get("pratica", "Respire por 2 minutos, organize prioridades e faca pausas.")
	parts.extend(
		[
			"- Passo 1: Ore por 2 minutos e entregue suas preocupacoes a Deus.",
			"- Passo 2: Escolha 3 prioridades do dia e execute uma por vez.",
			f"- Passo 3: Aplique esta pratica: {pratica}",
			"",
			"Frase externa para levar no bolso",
			f"\"{quote.get('text', 'Siga firme no proximo passo.')}\" - {quote.get('author', 'Autor desconhecido')}",
			"",
			"Obs: A API OpenAI retornou quota insuficiente (429). Assim que regularizar billing/quota, o modo completo volta automaticamente.",
		]
	)

	if reason:
		parts.append(f"Detalhe tecnico: {reason}")

	return "\n".join(parts)


def process_checkin(
	como_me_sinto_hoje: str,
	como_acordei: str,
	o_que_passou_ontem: str,
	atividades_de_hoje: str,
) -> str:
	if not os.getenv("OPENAI_API_KEY"):
		raise RuntimeError(
			"OPENAI_API_KEY nao encontrada. Configure no arquivo .env na raiz do projeto."
		)

	context_payload = prepare_full_context(
		como_me_sinto_hoje=como_me_sinto_hoje,
		como_acordei=como_acordei,
		o_que_passou_ontem=o_que_passou_ontem,
		atividades_de_hoje=atividades_de_hoje,
	)

	external_signals = compose_external_signals(context_payload.get("detected_theme", "sabedoria"))
	context_payload["external_signals"] = external_signals

	user_payload = {
		"como_me_sinto_hoje": como_me_sinto_hoje,
		"como_acordei": como_acordei,
		"o_que_passou_ontem": o_que_passou_ontem,
		"atividades_de_hoje": atividades_de_hoje,
		"detected_theme": context_payload.get("detected_theme", "sabedoria"),
		"bible_data": context_payload.get("bible_data", {}),
		"neuroscience_data": context_payload.get("neuroscience_data", {}),
		"external_signals": context_payload.get("external_signals", {}),
	}

	agents = create_agents()
	tasks = create_tasks(agents=agents, user_payload=user_payload)

	crew = Crew(
		agents=list(agents.values()),
		tasks=tasks,
		process=Process.sequential,
		verbose=False,
	)

	try:
		result = crew.kickoff(inputs=user_payload)
		return str(result)
	except Exception as error:
		if _is_quota_or_rate_limit_error(error):
			return _build_offline_response(context_payload=context_payload, reason=str(error))
		raise
