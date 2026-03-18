from typing import Any, Dict, List

import requests
from llama_index.core import Document, SummaryIndex


def fetch_news(topic: str, max_articles: int = 12) -> List[Dict[str, Any]]:
	"""Fetch recent news-like stories from the public Hacker News Algolia API."""
	safe_topic = topic.strip() or "inteligencia artificial"
	limit = max(3, min(max_articles, 30))
	url = (
		"https://hn.algolia.com/api/v1/search_by_date"
		f"?query={safe_topic}&tags=story&hitsPerPage={limit}"
	)

	response = requests.get(url, timeout=12)
	response.raise_for_status()
	payload = response.json()
	hits = payload.get("hits", []) if isinstance(payload, dict) else []

	items: List[Dict[str, Any]] = []
	for hit in hits:
		title = hit.get("title") or hit.get("story_title") or "Sem titulo"
		url_ref = hit.get("url") or hit.get("story_url") or ""
		author = hit.get("author") or "desconhecido"
		points = hit.get("points") or 0
		created_at = hit.get("created_at") or ""

		items.append(
			{
				"title": str(title),
				"url": str(url_ref),
				"author": str(author),
				"points": points,
				"created_at": str(created_at),
			}
		)

	return items


def fetch_world_news(topic: str, max_articles: int = 12) -> List[Dict[str, Any]]:
	"""Fetch world-news articles from GDELT DOC API (public, no key required)."""
	safe_topic = topic.strip() or "world"
	limit = max(3, min(max_articles, 30))
	url = (
		"https://api.gdeltproject.org/api/v2/doc/doc"
		f"?query={safe_topic}&mode=ArtList&maxrecords={limit}&format=json&sort=DateDesc"
	)

	try:
		response = requests.get(url, timeout=12)
		response.raise_for_status()
		payload = response.json()
		articles = payload.get("articles", []) if isinstance(payload, dict) else []

		items: List[Dict[str, Any]] = []
		for article in articles:
			title = article.get("title") or "Sem titulo"
			url_ref = article.get("url") or ""
			domain = article.get("domain") or "fonte-desconhecida"
			seendate = article.get("seendate") or ""

			items.append(
				{
					"title": str(title),
					"url": str(url_ref),
					"author": str(domain),
					"points": 0,
					"created_at": str(seendate),
					"source": "gdelt",
				}
			)

		return items
	except Exception:
		return []


def build_documents(news_items: List[Dict[str, Any]], topic: str) -> List[Document]:
	documents: List[Document] = []
	for idx, item in enumerate(news_items, start=1):
		content = (
			f"Tema pesquisado: {topic}\n"
			f"Noticia {idx}: {item.get('title', '')}\n"
			f"Autor: {item.get('author', '')}\n"
			f"Pontos: {item.get('points', 0)}\n"
			f"Data: {item.get('created_at', '')}\n"
			f"Fonte: {item.get('source', 'hn_algolia')}\n"
			f"URL: {item.get('url', '')}"
		)
		documents.append(Document(text=content, metadata={"source": item.get("source", "hn_algolia")}))
	return documents


def build_news_index(topic: str, max_articles: int = 12) -> tuple[SummaryIndex, List[Dict[str, Any]]]:
	hn_items = fetch_news(topic=topic, max_articles=max_articles)
	world_items = fetch_world_news(topic=topic, max_articles=max_articles)

	# Mix sources to reduce tech bias and improve global-topic coverage.
	items = (world_items[: max_articles // 2] + hn_items[: max_articles // 2])[:max_articles]

	if not items:
		fallback_item = {
			"title": f"Sem resultados recentes para {topic}",
			"url": "",
			"author": "sistema",
			"points": 0,
			"created_at": "",
			"source": "fallback",
		}
		items = [fallback_item]

	docs = build_documents(news_items=items, topic=topic)
	index = SummaryIndex.from_documents(docs)
	return index, items
