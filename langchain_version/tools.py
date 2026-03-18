import json
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================
# Aqui definimos onde estamos e onde ficam os arquivos JSON.
# Isso evita usar caminhos "soltos" no código e deixa tudo
# mais fácil de manter.
# ============================================================

# Pasta atual: langchain_version/
CURRENT_DIR = Path(__file__).resolve().parent

# Pasta raiz do projeto: neurodevocional-ai/
PROJECT_ROOT = CURRENT_DIR.parent

# Pasta onde estão os arquivos de base do projeto
DATA_DIR = PROJECT_ROOT / "data"

# Arquivos usados como base de conhecimento
BIBLE_TOPICS_FILE = DATA_DIR / "bible_topics.json"
NEUROSCIENCE_TOPICS_FILE = DATA_DIR / "neuroscience_topics.json"
DEVOTIONAL_EXAMPLES_FILE = DATA_DIR / "devotional_examples.json"


# ============================================================
# FUNÇÕES DE LEITURA DOS ARQUIVOS JSON
# ============================================================
# Essas funções têm uma responsabilidade bem clara:
# abrir os arquivos JSON e devolver os dados em formato Python.
#
# Exemplo:
# - JSON com temas bíblicos -> vira um dicionário
# - JSON com temas de neurociência -> vira um dicionário
# ============================================================

def load_json_file(file_path: Path) -> Any:
    """
    Lê um arquivo JSON e devolve o conteúdo convertido para Python.

    Parâmetros:
        file_path (Path): caminho do arquivo JSON.

    Retorno:
        Any: pode ser dict, list, etc., dependendo do conteúdo do arquivo.

    Por que essa função existe?
    Porque assim evitamos repetir o mesmo código de abertura de arquivo
    em vários lugares do projeto.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_bible_topics() -> Dict[str, Any]:
    """
    Carrega os temas bíblicos do arquivo bible_topics.json.

    Retorno:
        Dict[str, Any]: dicionário com os temas bíblicos.
    """
    return load_json_file(BIBLE_TOPICS_FILE)


def load_neuroscience_topics() -> Dict[str, Any]:
    """
    Carrega os temas de neurociência do arquivo neuroscience_topics.json.

    Retorno:
        Dict[str, Any]: dicionário com os temas de neurociência.
    """
    return load_json_file(NEUROSCIENCE_TOPICS_FILE)


def load_devotional_examples() -> List[Dict[str, Any]]:
    """
    Carrega exemplos de entrada e saída do arquivo devotional_examples.json.

    Retorno:
        List[Dict[str, Any]]: lista com exemplos.
    """
    return load_json_file(DEVOTIONAL_EXAMPLES_FILE)


# ============================================================
# CONSTRUÇÃO DO CONTEXTO DO USUÁRIO
# ============================================================
# O usuário vai preencher vários campos na interface:
# - como está se sentindo hoje
# - como acordou
# - o que passou ontem
# - atividades de hoje
#
# Para facilitar a análise, juntamos tudo em um único texto.
# Esse texto depois será usado para detectar o tema principal.
# ============================================================

def build_user_context(
    como_me_sinto_hoje: str,
    como_acordei: str,
    o_que_passou_ontem: str,
    atividades_de_hoje: str
) -> str:
    """
    Monta um texto único com todas as informações fornecidas pelo usuário.

    Parâmetros:
        como_me_sinto_hoje (str): sentimento atual do usuário.
        como_acordei (str): como o usuário acordou.
        o_que_passou_ontem (str): resumo do dia anterior.
        atividades_de_hoje (str): compromissos ou tarefas do dia.

    Retorno:
        str: texto consolidado com todo o contexto.
    """
    return f"""
    Como me sinto hoje: {como_me_sinto_hoje}
    Como acordei: {como_acordei}
    O que passou ontem: {o_que_passou_ontem}
    Atividades de hoje: {atividades_de_hoje}
    """.strip()


# ============================================================
# MAPA DE PALAVRAS-CHAVE PARA TEMAS
# ============================================================
# Aqui criamos uma lógica simples para identificar o tema
# principal com base em palavras do relato do usuário.
#
# Exemplo:
# se aparecer "ansioso", "preocupado" ou "agitado",
# o sistema entende que o tema pode ser "ansiedade".
#
# Essa é uma forma simples e controlada de começar.
# Depois, se quiser, podemos melhorar isso com LLM ou embeddings.
# ============================================================

THEME_KEYWORDS = {
    "ansiedade": [
        "ansioso", "ansiedade", "preocupado", "preocupação",
        "agitado", "apreensivo", "nervoso", "pressão", "sobrecarregado"
    ],
    "medo": [
        "medo", "inseguro", "receio", "assustado", "temor", "travado"
    ],
    "cansaco": [
        "cansado", "exausto", "sem energia", "esgotado", "sono",
        "desanimado", "sobrecarregado", "fatigado"
    ],
    "foco": [
        "foco", "distraído", "procrastinando", "procrastinação",
        "disperso", "organização", "produtividade", "atenção"
    ],
    "sabedoria": [
        "sabedoria", "decisão", "direção", "escolha", "dúvida",
        "discernimento", "entendimento", "orientação"
    ]
}


def normalize_text(text: str) -> str:
    """
    Normaliza o texto para facilitar comparação simples.

    Aqui estamos apenas:
    - deixando tudo minúsculo
    - removendo espaços extras

    Parâmetros:
        text (str): texto de entrada.

    Retorno:
        str: texto normalizado.
    """
    return " ".join(text.lower().split())


def detect_theme(user_context: str) -> str:
    """
    Detecta o tema principal a partir do texto do usuário.

    Como funciona:
    - o texto é normalizado
    - percorremos cada tema e suas palavras-chave
    - contamos quantas palavras daquele tema aparecem
    - o tema com mais ocorrências vence

    Parâmetros:
        user_context (str): texto consolidado com o contexto do usuário.

    Retorno:
        str: nome do tema principal identificado.
             Se nada for encontrado, devolvemos 'sabedoria' como fallback.

    Observação:
    Esse método é simples, mas muito útil para começar.
    """
    normalized_context = normalize_text(user_context)

    scores = {theme: 0 for theme in THEME_KEYWORDS.keys()}

    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized_context:
                scores[theme] += 1

    # Pega o tema com maior pontuação
    detected_theme = max(scores, key=scores.get)

    # Se nenhum tema teve pontuação, usamos "sabedoria" como tema padrão
    if scores[detected_theme] == 0:
        return "sabedoria"

    return detected_theme


# ============================================================
# BUSCA DE DADOS DO TEMA
# ============================================================
# Depois que descobrimos o tema principal, usamos esse tema
# para buscar informações nos arquivos JSON.
# ============================================================

def get_bible_theme_data(theme: str) -> Dict[str, Any]:
    """
    Busca os dados bíblicos de um tema específico.

    Parâmetros:
        theme (str): nome do tema.

    Retorno:
        Dict[str, Any]: dados daquele tema no bible_topics.json.
                        Se não encontrar, retorna dicionário vazio.
    """
    bible_topics = load_bible_topics()
    return bible_topics.get(theme, {})


def get_neuroscience_theme_data(theme: str) -> Dict[str, Any]:
    """
    Busca os dados de neurociência de um tema específico.

    Parâmetros:
        theme (str): nome do tema.

    Retorno:
        Dict[str, Any]: dados daquele tema no neuroscience_topics.json.
                        Se não encontrar, retorna dicionário vazio.
    """
    neuroscience_topics = load_neuroscience_topics()
    return neuroscience_topics.get(theme, {})


# ============================================================
# FUNÇÃO PRINCIPAL DE PREPARAÇÃO DE CONTEXTO
# ============================================================
# Essa função é uma das mais importantes do arquivo.
# Ela reúne tudo:
# - monta o texto do usuário
# - detecta o tema
# - busca os dados bíblicos
# - busca os dados de neurociência
#
# No fim, ela devolve um dicionário organizado.
# Esse dicionário depois será usado pelo app.py para gerar
# a resposta final com a OpenAI.
# ============================================================

def prepare_devotional_context(
    como_me_sinto_hoje: str,
    como_acordei: str,
    o_que_passou_ontem: str,
    atividades_de_hoje: str
) -> Dict[str, Any]:
    """
    Prepara todo o contexto necessário para a geração do devocional.

    Parâmetros:
        como_me_sinto_hoje (str)
        como_acordei (str)
        o_que_passou_ontem (str)
        atividades_de_hoje (str)

    Retorno:
        Dict[str, Any]: estrutura organizada com:
            - contexto completo do usuário
            - tema principal detectado
            - base bíblica do tema
            - base de neurociência do tema
    """
    user_context = build_user_context(
        como_me_sinto_hoje=como_me_sinto_hoje,
        como_acordei=como_acordei,
        o_que_passou_ontem=o_que_passou_ontem,
        atividades_de_hoje=atividades_de_hoje
    )

    detected_theme = detect_theme(user_context)
    bible_data = get_bible_theme_data(detected_theme)
    neuroscience_data = get_neuroscience_theme_data(detected_theme)

    return {
        "user_context": user_context,
        "detected_theme": detected_theme,
        "bible_data": bible_data,
        "neuroscience_data": neuroscience_data
    }


# ============================================================
# BLOCO DE TESTE LOCAL
# ============================================================
# Esse trecho só executa se você rodar este arquivo diretamente.
# É ótimo para testar rápido sem precisar abrir o Streamlit ainda.
#
# Exemplo no terminal:
# python langchain_version/tools.py
# ============================================================

if __name__ == "__main__":
    result = prepare_devotional_context(
        como_me_sinto_hoje="Estou ansioso e preocupado com o dia de hoje",
        como_acordei="Acordei cansado e sem muita energia",
        o_que_passou_ontem="Ontem foi um dia puxado e dormi tarde",
        atividades_de_hoje="Tenho prova, reunião e muitas tarefas"
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))