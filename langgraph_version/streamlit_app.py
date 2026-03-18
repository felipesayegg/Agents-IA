import streamlit as st

try:
	from .app import run_trip_planner
except ImportError:
	from app import run_trip_planner


st.set_page_config(page_title="Travel Planner - LangGraph", layout="wide")
st.title("Travel Planner AI - LangGraph")
st.caption("Agente de planejamento de viagens com APIs externas sem chave")

if "history" not in st.session_state:
	st.session_state.history = []

with st.sidebar:
	st.subheader("Configuracao")
	style = st.selectbox("Estilo da viagem", ["economico", "equilibrado", "conforto"], index=1)
	if st.button("Limpar historico"):
		st.session_state.history = []
		st.success("Historico limpo.")

destination = st.text_input("Destino", placeholder="Ex: Lisboa")
col1, col2 = st.columns(2)
with col1:
	trip_days = st.slider("Dias de viagem", min_value=1, max_value=10, value=4)
with col2:
	budget = st.number_input("Orcamento total (USD)", min_value=0.0, value=700.0, step=50.0)

interests = st.text_area(
	"Interesses",
	placeholder="Ex: gastronomia local, museus, natureza, passeios a pe",
	height=100,
)

if st.button("Montar roteiro com LangGraph", type="primary"):
	if not destination.strip():
		st.warning("Informe um destino para continuar.")
	else:
		with st.spinner("Buscando dados externos e montando plano..."):
			report = run_trip_planner(
				destination=destination,
				trip_days=trip_days,
				budget=budget,
				interests=interests,
				travel_style=style,
			)
			st.session_state.history.append(
				{
					"input": f"{destination} | {trip_days} dias | USD {budget} | {style} | {interests}",
					"output": report,
				}
			)
			st.markdown("### Seu plano de viagem")
			st.write(report)

st.markdown("---")
st.subheader("Historico")
if not st.session_state.history:
	st.info("Sem planejamentos nesta sessao.")
else:
	for i, item in enumerate(reversed(st.session_state.history), start=1):
		st.markdown(f"**Planejamento {i}**")
		st.markdown(f"**Entrada:** {item['input']}")
		st.markdown(f"**Saida:** {item['output']}")
		st.markdown("---")
