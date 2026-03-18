from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

try:
	from .app import process_checkin
except ImportError:
	from app import process_checkin


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(page_title="Neurodevocional AI - CrewAI", layout="wide")
st.title("Neurodevocional AI - CrewAI")
st.caption("Check-in emocional com orquestracao multiagente")

if "chat_log" not in st.session_state:
	st.session_state.chat_log = []

col_left, col_right = st.columns([3, 1])
with col_right:
	if st.button("Nova conversa", use_container_width=True):
		st.session_state.chat_log = []
		st.success("Historico resetado.")

st.subheader("Check-in guiado")
como_me_sinto_hoje = st.text_area("Como me sinto hoje", height=100)
como_acordei = st.text_area("Como acordei", height=80)
o_que_passou_ontem = st.text_area("O que passou ontem", height=100)
atividades_de_hoje = st.text_area("Atividades de hoje", height=100)

if st.button("Gerar orientacao com CrewAI", type="primary"):
	if not como_me_sinto_hoje.strip():
		st.warning("Preencha pelo menos o campo 'Como me sinto hoje'.")
	else:
		with st.spinner("Orquestrando agentes..."):
			resposta = process_checkin(
				como_me_sinto_hoje=como_me_sinto_hoje,
				como_acordei=como_acordei,
				o_que_passou_ontem=o_que_passou_ontem,
				atividades_de_hoje=atividades_de_hoje,
			)
			st.session_state.chat_log.append(
				{
					"usuario": (
						f"Check-in: {como_me_sinto_hoje} | {como_acordei} | "
						f"{o_que_passou_ontem} | {atividades_de_hoje}"
					),
					"assistente": resposta,
				}
			)
			st.markdown("### Resposta")
			st.write(resposta)

st.markdown("---")
st.subheader("Historico")
if not st.session_state.chat_log:
	st.info("Ainda sem interacoes nesta sessao.")
else:
	for idx, item in enumerate(reversed(st.session_state.chat_log), start=1):
		st.markdown(f"**Interacao {idx}**")
		st.markdown(f"**Usuario:** {item['usuario']}")
		st.markdown(f"**Assistente:** {item['assistente']}")
		st.markdown("---")
