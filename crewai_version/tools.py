import json
from urllib.parse import quote
from typing import Any, Dict, List

import requests

try:
	from .core.context_builder import (
		load_bible_topics,
		load_neuroscience_topics,
		prepare_devotional_context,
	)
except ImportError:
	from core.context_builder import (  # type: ignore
		load_bible_topics,
		load_neuroscience_topics,
		prepare_devotional_context,
	)

try:
	from crewai.tools import tool
except Exception:  # pragma: no cover - compatibility fallback
	tool = None


def prepare_full_context(
	como_me_sinto_hoje: str,
	como_acordei: str,
	o_que_passou_ontem: str,
	atividades_de_hoje: str,
) -> Dict[str, Any]:
	return prepare_devotional_context(
		como_me_sinto_hoje=como_me_sinto_hoje,
		como_acordei=como_acordei,
		o_que_passou_ontem=o_que_passou_ontem,
		atividades_de_hoje=atividades_de_hoje,
	)


def get_bible_theme_data(theme: str) -> Dict[str, Any]:
	return load_bible_topics().get(theme, {})


def get_neuroscience_theme_data(theme: str) -> Dict[str, Any]:
	return load_neuroscience_topics().get(theme, {})


THEME_TO_VERSE = {
	"ansiedade": "Filipenses 4:6-7",
	"medo": "Isaías 41:10",
	"cansaco": "Mateus 11:28",
	"foco": "Colossenses 3:23",
	"sabedoria": "Tiago 1:5",
}


def fetch_external_quote() -> Dict[str, str]:
	"""Fetch a short quote from an external public API (no key required)."""
	url = "https://zenquotes.io/api/random"
	try:
		response = requests.get(url, timeout=8)
		response.raise_for_status()
		payload = response.json()
		if isinstance(payload, list) and payload:
			item = payload[0]
			return {
				"text": item.get("q", ""),
				"author": item.get("a", "Autor desconhecido"),
				"source": "zenquotes.io",
			}
	except Exception:
		pass
	return {
		"text": "A consistencia no hoje constrói a transformacao do amanha.",
		"author": "Fonte local (fallback)",
		"source": "local-fallback",
	}


def fetch_external_bible_verse(theme: str) -> Dict[str, str]:
	"""Fetch a Bible verse from a public API (no key required), based on detected theme."""
	reference = THEME_TO_VERSE.get(theme, "Tiago 1:5")
	url = f"https://bible-api.com/{quote(reference)}"
	try:
		response = requests.get(url, timeout=8)
		response.raise_for_status()
		payload = response.json()
		return {
			"reference": payload.get("reference", reference),
			"text": payload.get("text", "").strip(),
			"source": "bible-api.com",
		}
	except Exception:
		return {
			"reference": reference,
			"text": "Permaneça firme: um passo de cada vez, com fe e lucidez.",
			"source": "local-fallback",
		}


def compose_external_signals(theme: str) -> Dict[str, Any]:
	"""Combine external quote and external verse into a single payload."""
	return {
		"quote": fetch_external_quote(),
		"verse": fetch_external_bible_verse(theme),
	}


if tool is not None:

	@tool("prepare_full_context")
	def prepare_full_context_tool(
		como_me_sinto_hoje: str,
		como_acordei: str,
		o_que_passou_ontem: str,
		atividades_de_hoje: str,
	) -> str:
		"""Transforma o check-in do usuario em contexto estruturado com tema detectado."""
		payload = prepare_full_context(
			como_me_sinto_hoje=como_me_sinto_hoje,
			como_acordei=como_acordei,
			o_que_passou_ontem=o_que_passou_ontem,
			atividades_de_hoje=atividades_de_hoje,
		)
		return json.dumps(payload, ensure_ascii=False)


	@tool("get_bible_theme_data")
	def get_bible_theme_data_tool(theme: str) -> str:
		"""Retorna versiculos e mensagem biblica para um tema."""
		return json.dumps(get_bible_theme_data(theme), ensure_ascii=False)


	@tool("get_neuroscience_theme_data")
	def get_neuroscience_theme_data_tool(theme: str) -> str:
		"""Retorna explicacao e pratica de neurociencia para um tema."""
		return json.dumps(get_neuroscience_theme_data(theme), ensure_ascii=False)


	@tool("get_external_signals")
	def get_external_signals_tool(theme: str) -> str:
		"""Busca frase e versiculo em APIs externas publicas sem chave."""
		return json.dumps(compose_external_signals(theme), ensure_ascii=False)


def get_crewai_tools() -> List[Any]:
	if tool is None:
		return []
	return [
		prepare_full_context_tool,
		get_bible_theme_data_tool,
		get_neuroscience_theme_data_tool,
		get_external_signals_tool,
	]
