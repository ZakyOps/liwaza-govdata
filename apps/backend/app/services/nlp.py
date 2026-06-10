from __future__ import annotations

import re
import unicodedata

from lingua import Language as LinguaLanguage
from lingua import LanguageDetectorBuilder

SupportedLanguage = str

DEFAULT_LANGUAGE: SupportedLanguage = "fr"
DEFAULT_SEARCH_QUERY = "cote d'ivoire"
DEFAULT_YEAR_RANGE = (2020, 2023)

LANGUAGE_DETECTOR = LanguageDetectorBuilder.from_languages(
    LinguaLanguage.FRENCH,
    LinguaLanguage.ENGLISH,
).build()

FRENCH_WORDS = [
    "bonjour",
    "salut",
    "trouve",
    "cherche",
    "montre",
    "affiche",
    "resume",
    "compare",
    "donnee",
    "donnees",
    "colonnes",
    "schema",
    "ligne",
    "lignes",
    "quel",
    "quelle",
    "quels",
    "quelles",
    "comment",
    "pourquoi",
    "education",
    "sante",
    "economie",
]

ENGLISH_WORDS = [
    "hello",
    "hi",
    "find",
    "search",
    "show",
    "summarize",
    "summary",
    "compare",
    "dataset",
    "datasets",
    "data",
    "columns",
    "schema",
    "rows",
    "which",
    "what",
    "how",
    "why",
    "education",
    "health",
    "economy",
]

STRONG_FRENCH_WORDS = ["bonjour", "trouve", "cherche", "montre", "affiche", "resume"]
STRONG_ENGLISH_WORDS = ["hello", "find", "search", "show", "summarize"]
FRENCH_ACCENTS = ["é", "è", "ê", "à", "ç", "ù"]

TOPIC_ALIASES: dict[str, tuple[str, str, list[str]]] = {
    "education": (
        "education",
        "education",
        ["education", "éducation", "ecole", "école", "scolaire", "enseignants"],
    ),
    "health": (
        "sante",
        "health",
        ["sante", "santé", "health", "hopital", "hôpital"],
    ),
    "economy": (
        "economie",
        "economy",
        ["economie", "économie", "economic", "economy", "investissement", "pib"],
    ),
    "budget": (
        "budget",
        "budget",
        ["budget", "fiscal", "taxe", "impot", "impôt"],
    ),
}

SEARCH_COMMAND_WORDS = [
    "trouve",
    "cherche",
    "find",
    "search",
    "datasets",
    "jeux de donnees",
    "jeux de données",
]

SEARCH_FILLER_WORDS = [
    "lies a",
    "lies à",
    "liés a",
    "liés à",
    "liees a",
    "liées à",
    "sur",
    "about",
    "les",
    "l'",
]


def detect_language(message: str) -> SupportedLanguage:
    detected_language = LANGUAGE_DETECTOR.detect_language_of(message)
    if detected_language == LinguaLanguage.FRENCH:
        return "fr"
    if detected_language == LinguaLanguage.ENGLISH:
        return "en"

    return _detect_language_with_lexical_fallback(message)


def detect_intent(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ["compare", "comparaison", "between", "entre"]):
        return "compare"
    if any(word in lowered for word in ["schema", "schéma", "colonnes", "columns", "fields"]):
        return "schema"
    if any(word in lowered for word in ["ligne", "lignes", "rows", "sample"]):
        return "rows"
    if any(word in lowered for word in ["resume", "résume", "summary", "summarize"]):
        return "summary"
    if any(word in lowered for word in ["graph", "chart", "visualise", "visualize"]):
        return "chart"
    return "search"


def extract_years(message: str) -> tuple[int, int]:
    years = [int(match) for match in re.findall(r"\b(19\d{2}|20\d{2})\b", message)]
    if len(years) >= 2:
        return min(years[:2]), max(years[:2])
    return DEFAULT_YEAR_RANGE


def extract_search_query(message: str, language: SupportedLanguage = DEFAULT_LANGUAGE) -> str:
    lowered = message.lower()

    topic_query = _topic_query_from_alias(lowered, language)
    if topic_query:
        return topic_query

    cleaned_query = _remove_search_noise(lowered)
    return cleaned_query or DEFAULT_SEARCH_QUERY


def _detect_language_with_lexical_fallback(message: str) -> SupportedLanguage:
    lowered = message.lower()
    normalized = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
    french_score = _score_language(normalized, FRENCH_WORDS, STRONG_FRENCH_WORDS)
    english_score = _score_language(normalized, ENGLISH_WORDS, STRONG_ENGLISH_WORDS)

    if french_score == english_score:
        return DEFAULT_LANGUAGE if any(char in lowered for char in FRENCH_ACCENTS) else "en"
    return DEFAULT_LANGUAGE if french_score > english_score else "en"


def _score_language(message: str, words: list[str], strong_words: list[str]) -> int:
    score = sum(1 for word in words if re.search(rf"\b{re.escape(word)}\b", message))
    score += sum(2 for word in strong_words if re.search(rf"\b{re.escape(word)}\b", message))
    return score


def _topic_query_from_alias(message: str, language: SupportedLanguage) -> str | None:
    for french_query, english_query, aliases in TOPIC_ALIASES.values():
        if any(alias in message for alias in aliases):
            return french_query if language == "fr" else english_query
    return None


def _remove_search_noise(message: str) -> str:
    cleaned = message
    for prefix in SEARCH_COMMAND_WORDS:
        cleaned = cleaned.replace(prefix, " ")
    for filler in SEARCH_FILLER_WORDS:
        cleaned = cleaned.replace(filler, " ")
    return " ".join(cleaned.split()).strip(" .?!")
