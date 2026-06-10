from app.services.chat import ChatService
from app.services.nlp import detect_intent, detect_language, extract_search_query, extract_years
from app.services.tools import ToolService


def test_detect_compare_intent():
    assert detect_intent("Compare les investissements entre 2020 et 2023") == "compare"


def test_extract_years():
    assert extract_years("entre 2020 et 2023") == (2020, 2023)


def test_extract_search_query_respects_english_language():
    assert extract_search_query("Search datasets about health", "en") == "health"


def test_detect_french_language():
    assert detect_language("Trouve les datasets education") == "fr"


def test_detect_french_greeting():
    assert detect_language("Bonjour, montre les données disponibles") == "fr"


def test_detect_english_language():
    assert detect_language("Search datasets about health") == "en"


def test_search_answer_returns_french_text():
    answer = ChatService._search_answer({"count": 40, "results": [{}, {}]}, "fr")
    assert "J'ai trouvé 2 datasets publics sur data.gouv.ci" in answer


def test_rejects_foreign_federated_dataset():
    dataset = {
        "title": "Annuaire de l'éducation",
        "description": "Données sur les établissements situés en France.",
        "origin": "https://www.data.gouv.fr/fr/datasets/annuaire-de-leducation/",
    }

    assert ToolService._is_cote_divoire_dataset(dataset) is False


def test_keeps_ivoirian_dataset():
    dataset = {
        "title": "Infrastructures par DRENA",
        "description": "Données sur les écoles en Côte d'Ivoire.",
        "origin": "Ministère de l'Education Nationale",
    }

    assert ToolService._is_cote_divoire_dataset(dataset) is True
