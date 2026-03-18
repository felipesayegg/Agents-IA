import json
from pathlib import Path
from typing import Any, Dict

CURRENT_DIR = Path(__file__).resolve().parent
CREWAI_DIR = CURRENT_DIR.parent
PROJECT_ROOT = CREWAI_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

BIBLE_TOPICS_FILE = DATA_DIR / "bible_topics.json"
NEUROSCIENCE_TOPICS_FILE = DATA_DIR / "neuroscience_topics.json"

THEME_KEYWORDS = {
    "ansiedade": [
        "ansioso",
        "ansiedade",
        "preocupado",
        "preocupacao",
        "agitado",
        "apreensivo",
        "nervoso",
        "pressao",
        "sobrecarregado",
    ],
    "medo": ["medo", "inseguro", "receio", "assustado", "temor", "travado"],
    "cansaco": [
        "cansado",
        "exausto",
        "sem energia",
        "esgotado",
        "sono",
        "desanimado",
        "fatigado",
    ],
    "foco": [
        "foco",
        "distraido",
        "procrastinando",
        "procrastinacao",
        "disperso",
        "organizacao",
        "produtividade",
        "atencao",
    ],
    "sabedoria": [
        "sabedoria",
        "decisao",
        "direcao",
        "escolha",
        "duvida",
        "discernimento",
        "entendimento",
        "orientacao",
    ],
}


def load_json_file(file_path: Path) -> Any:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_bible_topics() -> Dict[str, Any]:
    return load_json_file(BIBLE_TOPICS_FILE)


def load_neuroscience_topics() -> Dict[str, Any]:
    return load_json_file(NEUROSCIENCE_TOPICS_FILE)


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def build_user_context(
    como_me_sinto_hoje: str,
    como_acordei: str,
    o_que_passou_ontem: str,
    atividades_de_hoje: str,
) -> str:
    return (
        f"Como me sinto hoje: {como_me_sinto_hoje}\n"
        f"Como acordei: {como_acordei}\n"
        f"O que passou ontem: {o_que_passou_ontem}\n"
        f"Atividades de hoje: {atividades_de_hoje}"
    )


def detect_theme(user_context: str) -> str:
    normalized_context = normalize_text(user_context)
    scores = {theme: 0 for theme in THEME_KEYWORDS}

    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized_context:
                scores[theme] += 1

    detected_theme = max(scores, key=scores.get)
    return detected_theme if scores[detected_theme] > 0 else "sabedoria"


def prepare_devotional_context(
    como_me_sinto_hoje: str,
    como_acordei: str,
    o_que_passou_ontem: str,
    atividades_de_hoje: str,
) -> Dict[str, Any]:
    user_context = build_user_context(
        como_me_sinto_hoje=como_me_sinto_hoje,
        como_acordei=como_acordei,
        o_que_passou_ontem=o_que_passou_ontem,
        atividades_de_hoje=atividades_de_hoje,
    )
    detected_theme = detect_theme(user_context)

    bible_topics = load_bible_topics()
    neuroscience_topics = load_neuroscience_topics()

    return {
        "user_context": user_context,
        "detected_theme": detected_theme,
        "bible_data": bible_topics.get(detected_theme, {}),
        "neuroscience_data": neuroscience_topics.get(detected_theme, {}),
    }
