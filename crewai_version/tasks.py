from crewai import Task


def create_tasks(agents: dict, user_payload: dict) -> list[Task]:
	analyst_task = Task(
		description=(
			"Analise o check-in emocional do usuario abaixo e identifique o tema principal.\n\n"
			"Check-in:\n"
			"- Como me sinto hoje: {como_me_sinto_hoje}\n"
			"- Como acordei: {como_acordei}\n"
			"- O que passou ontem: {o_que_passou_ontem}\n"
			"- Atividades de hoje: {atividades_de_hoje}\n\n"
			"Use as ferramentas para enriquecer o entendimento do contexto.\n"
			"Entregue:\n"
			"1) Tema principal\n"
			"2) Sinais emocionais observados\n"
			"3) Riscos para o dia (curto, sem dramatizar)"
		),
		expected_output=(
			"Resumo analitico com tema principal, sinais emocionais e riscos do dia "
			"em linguagem acolhedora e objetiva."
		),
		agent=agents["emotional_analyst"],
	)

	guide_task = Task(
		description=(
			"Com base no contexto estruturado abaixo e na analise anterior, crie uma resposta final "
			"em portugues com tom humano, menos engessado e sem parecer template fixo.\n"
			"Use este roteiro com titulos criativos:\n"
			"- Raio-X emocional de hoje\n"
			"- Fio condutor do dia\n"
			"- Palavra biblica em movimento\n"
			"- Neuroacao de bolso\n"
			"- Mini plano pratico (3 micro-acoes)\n"
			"- Fechamento com sinal externo (frase/versiculo vindo das APIs externas)\n\n"
			"Evite repetir literalmente o formato usado na versao LangChain.\n"
			"Contexto detectado: {detected_theme}\n"
			"Dados biblicos: {bible_data}\n"
			"Dados de neurociencia: {neuroscience_data}\n"
			"Sinais externos de API: {external_signals}"
		),
		expected_output=(
			"Resposta neurodevocional autoral, com linguagem acolhedora, estrutura diferenciada e aplicacao pratica para o dia."
		),
		agent=agents["neurodevotional_guide"],
		context=[analyst_task],
	)

	_ = user_payload
	return [analyst_task, guide_task]
