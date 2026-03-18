from typing import Any, Dict, List

try:
	from .index_builder import build_news_index
	from .query_engine import generate_news_report
except ImportError:
	from index_builder import build_news_index
	from query_engine import generate_news_report


def run_news_analysis(topic: str, max_articles: int = 12) -> tuple[str, List[Dict[str, Any]]]:
	index, news_items = build_news_index(topic=topic, max_articles=max_articles)
	report = generate_news_report(index=index, topic=topic, news_items=news_items)
	return report, news_items
