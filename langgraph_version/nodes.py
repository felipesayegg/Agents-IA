import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

try:
	from .state import TripPlannerState
except ImportError:
	from state import TripPlannerState


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def enrich_destination_node(state: TripPlannerState) -> TripPlannerState:
	destination = state.get("destination", "").strip()
	if not destination:
		return {**state, "error": "Destino vazio."}

	url = (
		"https://geocoding-api.open-meteo.com/v1/search"
		f"?name={quote(destination)}&count=1&language=pt&format=json"
	)

	fallback = {
		"city": destination,
		"country": "Nao identificado",
		"latitude": 0.0,
		"longitude": 0.0,
		"timezone": "auto",
	}

	try:
		response = requests.get(url, timeout=10)
		response.raise_for_status()
		payload = response.json()
		results = payload.get("results", []) if isinstance(payload, dict) else []
		if not results:
			return {**state, "profile_data": fallback}

		place = results[0]
		return {
			**state,
			"profile_data": {
				"city": place.get("name", destination),
				"country": place.get("country", "Nao identificado"),
				"latitude": place.get("latitude", 0.0),
				"longitude": place.get("longitude", 0.0),
				"timezone": place.get("timezone", "auto"),
			},
		}
	except Exception:
		return {**state, "profile_data": fallback}


def weather_forecast_node(state: TripPlannerState) -> TripPlannerState:
	profile = state.get("profile_data", {})
	lat = profile.get("latitude", 0.0)
	lon = profile.get("longitude", 0.0)
	days = int(state.get("trip_days", 3))
	days = max(1, min(days, 7))

	if not lat and not lon:
		return {
			**state,
			"weather_data": {
				"summary": "Previsao indisponivel para este destino.",
				"source": "fallback",
			},
		}

	url = (
		"https://api.open-meteo.com/v1/forecast"
		f"?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
		f"&forecast_days={days}&timezone=auto"
	)

	try:
		response = requests.get(url, timeout=10)
		response.raise_for_status()
		payload = response.json()
		daily = payload.get("daily", {})
		max_t = daily.get("temperature_2m_max", [])
		min_t = daily.get("temperature_2m_min", [])
		rain = daily.get("precipitation_probability_max", [])
		dates = daily.get("time", [])

		bullets: List[str] = []
		for idx, date in enumerate(dates[:days]):
			tmax = max_t[idx] if idx < len(max_t) else "-"
			tmin = min_t[idx] if idx < len(min_t) else "-"
			prain = rain[idx] if idx < len(rain) else "-"
			bullets.append(f"{date}: max {tmax}C, min {tmin}C, chuva {prain}%")

		return {
			**state,
			"weather_data": {
				"summary": " | ".join(bullets) if bullets else "Sem detalhes de previsao.",
				"source": "open-meteo.com",
			},
		}
	except Exception:
		return {
			**state,
			"weather_data": {
				"summary": "Previsao indisponivel no momento.",
				"source": "fallback",
			},
		}


def attractions_node(state: TripPlannerState) -> TripPlannerState:
	destination = state.get("destination", "")
	interests = state.get("interests", "")
	query = f"{destination} {interests} turismo".strip()
	url = (
		"https://pt.wikipedia.org/w/api.php"
		f"?action=opensearch&search={quote(query)}&limit=5&namespace=0&format=json"
	)

	fallback = [
		{
			"title": f"Centro historico de {destination}",
			"description": "Sugerimos explorar areas centrais e culturais com caminhada guiada.",
			"link": "",
		}
	]

	try:
		response = requests.get(url, timeout=10)
		response.raise_for_status()
		payload = response.json()
		if not isinstance(payload, list) or len(payload) < 4:
			return {**state, "attractions_data": fallback}

		titles = payload[1]
		descriptions = payload[2]
		links = payload[3]

		items: List[Dict[str, str]] = []
		for idx, title in enumerate(titles):
			items.append(
				{
					"title": str(title),
					"description": str(descriptions[idx]) if idx < len(descriptions) else "",
					"link": str(links[idx]) if idx < len(links) else "",
				}
			)

		return {**state, "attractions_data": items or fallback}
	except Exception:
		return {**state, "attractions_data": fallback}


def cost_estimator_node(state: TripPlannerState) -> TripPlannerState:
	days = max(1, int(state.get("trip_days", 3)))
	budget = float(state.get("budget", 0.0))
	style = (state.get("travel_style", "equilibrado") or "equilibrado").lower()

	daily_map = {
		"economico": 60.0,
		"equilibrado": 110.0,
		"conforto": 180.0,
	}
	expected_daily = daily_map.get(style, 110.0)
	expected_total = expected_daily * days
	status = "dentro do esperado" if budget >= expected_total else "abaixo do recomendado"

	return {
		**state,
		"cost_data": {
			"expected_daily_usd": expected_daily,
			"expected_total_usd": expected_total,
			"provided_budget_usd": budget,
			"budget_status": status,
		},
	}


def _build_llm() -> ChatOpenAI:
	if not os.getenv("OPENAI_API_KEY"):
		raise RuntimeError("OPENAI_API_KEY nao encontrada no .env")
	return ChatOpenAI(model="gpt-4o-mini", temperature=0.5)


def planner_writer_node(state: TripPlannerState) -> TripPlannerState:
	if state.get("error"):
		return {**state, "final_report": f"Erro: {state['error']}"}

	llm = _build_llm()
	profile = state.get("profile_data", {})
	weather = state.get("weather_data", {})
	attractions = state.get("attractions_data", [])
	cost = state.get("cost_data", {})

	attractions_text = "\n".join(
		[f"- {item.get('title', '')}: {item.get('description', '')}" for item in attractions[:5]]
	)

	prompt = f"""
Voce e um agente estrategista de viagens.
Crie um roteiro claro, pratico e humano em portugues, evitando formato engessado.

Contexto da viagem:
- Destino: {profile.get('city', state.get('destination', ''))}, {profile.get('country', '')}
- Duracao: {state.get('trip_days', 3)} dias
- Orcamento informado (USD): {state.get('budget', 0)}
- Estilo de viagem: {state.get('travel_style', 'equilibrado')}
- Interesses: {state.get('interests', '')}

Dados externos coletados:
- Clima (Open-Meteo): {weather.get('summary', '')}
- Pontos de interesse (Wikipedia):
{attractions_text}

Estimativa de custo:
- Diario esperado (USD): {cost.get('expected_daily_usd', 0)}
- Total esperado (USD): {cost.get('expected_total_usd', 0)}
- Status do orcamento: {cost.get('budget_status', '')}

Entregue:
1) Visao geral da viagem em 3-4 linhas
2) Roteiro dia a dia
3) Top 5 experiencias sugeridas
4) Alerta de custo e como otimizar
5) Checklist final antes de embarcar
""".strip()

	response = llm.invoke(prompt)
	return {**state, "final_report": response.content}
