import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _offline_report(topic: str, news_items: List[Dict[str, Any]]) -> str:
	top_titles = news_items[:5]
	bullets = [f"- {item.get('title', 'Sem titulo')}" for item in top_titles]
	bullets_text = "\n".join(bullets)
	return (
		"Modo offline temporario (sem LLM).\n\n"
		f"Tema analisado: {topic}\n"
		"Principais manchetes encontradas:\n"
		f"{bullets_text}\n\n"
		"Leitura rapida:\n"
		"- O tema segue com alto volume de publicacoes recentes.\n"
		"- Ha oportunidades para monitorar subtemas especificos e evolucao semanal.\n"
		"- Recomenda-se acompanhar fontes com maior recorrencia de publicacao."
	)


def generate_news_report(index: Any, topic: str, news_items: List[Dict[str, Any]]) -> str:
	query = (
		"Gere um relatorio executivo em portugues com linguagem humana e objetiva. "
		"Estruture em: panorama geral, principais tendencias, sinais de risco/oportunidade, "
		"acoes praticas para os proximos 7 dias e 3 perguntas para monitoramento continuo."
	)

	if not os.getenv("OPENAI_API_KEY"):
		return _offline_report(topic=topic, news_items=news_items)

	llm = OpenAI(model="gpt-4o-mini", temperature=0.4)
	engine = index.as_query_engine(response_mode="tree_summarize", llm=llm)
	response = engine.query(query)
	return str(response)
