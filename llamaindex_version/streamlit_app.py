import streamlit as st

try:
	from .app import run_news_analysis
except ImportError:
	from app import run_news_analysis


st.set_page_config(page_title="News Analyzer - LlamaIndex", layout="wide")
st.title("News Analyzer AI - LlamaIndex")
st.caption("Analise e resumo de noticias com API externa sem chave")

if "history" not in st.session_state:
	st.session_state.history = []

col1, col2 = st.columns([3, 1])
with col2:
	if st.button("Limpar historico", use_container_width=True):
		st.session_state.history = []
		st.success("Historico limpo.")

topic = st.text_input("Tema para analisar noticias", value="inteligencia artificial")
max_articles = st.slider("Quantidade de noticias", min_value=5, max_value=25, value=12, step=1)

if st.button("Analisar noticias", type="primary"):
	with st.spinner("Coletando noticias e gerando relatorio..."):
		report, items = run_news_analysis(topic=topic, max_articles=max_articles)
		st.session_state.history.append(
			{
				"topic": topic,
				"items": items,
				"report": report,
			}
		)

		st.markdown("### Relatorio executivo")
		st.write(report)

		st.markdown("### Fontes coletadas")
		for i, item in enumerate(items[:10], start=1):
			title = item.get("title", "Sem titulo")
			url = item.get("url", "")
			if url:
				st.markdown(f"{i}. [{title}]({url})")
			else:
				st.markdown(f"{i}. {title}")

st.markdown("---")
st.subheader("Historico")
if not st.session_state.history:
	st.info("Nenhuma analise realizada nesta sessao.")
else:
	for idx, item in enumerate(reversed(st.session_state.history), start=1):
		st.markdown(f"**Analise {idx} - Tema:** {item['topic']}")
		st.markdown(f"**Resumo:** {item['report']}")
		st.markdown("---")
