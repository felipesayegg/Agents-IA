import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

try:
	from .app import process_chat_message, process_checkin, reset_conversation
except ImportError:
	from app import process_chat_message, process_checkin, reset_conversation


st.set_page_config(page_title="Neurodevocional AI - LangChain", layout="wide")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

st.title("Neurodevocional AI - LangChain Agent")
st.caption("Fluxo robusto: interface -> app -> agente -> tools -> dados JSON")


if "executor" not in st.session_state:
	st.session_state.executor = None

if "chat_log" not in st.session_state:
	st.session_state.chat_log = []


col_a, col_b = st.columns([3, 1])
with col_b:
	if st.button("Nova conversa", use_container_width=True):
		st.session_state.executor = reset_conversation()
		st.session_state.chat_log = []
		st.success("Memoria resetada. Nova conversa iniciada.")

if not os.getenv("OPENAI_API_KEY"):
	st.warning(
		"Configure OPENAI_API_KEY no arquivo .env na raiz de `neurodevocional-ai` "
		"para habilitar as respostas do agente."
	)


tab1, tab2 = st.tabs(["Check-in guiado", "Conversa livre"])


with tab1:
	st.subheader("Check-in do dia")
	como_me_sinto_hoje = st.text_area("Como me sinto hoje", height=100)
	como_acordei = st.text_area("Como acordei", height=80)
	o_que_passou_ontem = st.text_area("O que passou ontem", height=100)
	atividades_de_hoje = st.text_area("Atividades de hoje", height=100)

	if st.button("Gerar orientacao neurodevocional", type="primary"):
		if not como_me_sinto_hoje.strip():
			st.warning("Preencha pelo menos o campo 'Como me sinto hoje'.")
		else:
			with st.spinner("Gerando resposta com o agente..."):
				executor, resposta = process_checkin(
					executor=st.session_state.executor,
					como_me_sinto_hoje=como_me_sinto_hoje,
					como_acordei=como_acordei,
					o_que_passou_ontem=o_que_passou_ontem,
					atividades_de_hoje=atividades_de_hoje,
				)
				st.session_state.executor = executor
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


with tab2:
	st.subheader("Conversa livre")
	user_message = st.text_area("Digite sua mensagem", height=120)

	if st.button("Enviar mensagem"):
		if not user_message.strip():
			st.warning("Digite uma mensagem para continuar.")
		else:
			with st.spinner("Pensando..."):
				executor, resposta = process_chat_message(
					executor=st.session_state.executor,
					user_message=user_message,
				)
				st.session_state.executor = executor
				st.session_state.chat_log.append(
					{
						"usuario": user_message,
						"assistente": resposta,
					}
				)
				st.write(resposta)


st.markdown("---")
st.subheader("Historico da conversa")
if not st.session_state.chat_log:
	st.info("Ainda sem interacoes nesta sessao.")
else:
	for idx, item in enumerate(reversed(st.session_state.chat_log), start=1):
		st.markdown(f"**Interacao {idx}**")
		st.markdown(f"**Usuario:** {item['usuario']}")
		st.markdown(f"**Assistente:** {item['assistente']}")
		st.markdown("---")
