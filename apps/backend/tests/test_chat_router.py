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


def test_infers_year_and_numeric_fields_for_generic_comparison():
    rows = [
        {"annee_scolaire": 2020, "ecoles": 10, "_rand": 4},
        {"annee_scolaire": 2021, "ecoles": 12, "_rand": 5},
    ]

    assert ToolService._infer_comparison_fields(rows, "__auto__", "__auto__") == (
        "annee_scolaire",
        "ecoles",
    )


def test_infers_year_from_school_year_text():
    rows = [
        {"annee_scolaire": "2020-2021", "effectif_total": "1200", "enseignants_femmes": 2050},
        {"annee_scolaire": "2021-2022", "effectif_total": "1300", "enseignants_femmes": 2060},
    ]

    assert ToolService._infer_comparison_fields(rows, "__auto__", "__auto__") == (
        "annee_scolaire",
        "effectif_total",
    )
    assert ToolService._coerce_year("2020-2021") == 2020
    assert ToolService._coerce_number("1 300,5") == 1300.5


def test_compare_answer_handles_empty_values():
    answer = ChatService._compare_answer({"values": [], "absolute_change": None}, "fr")

    assert "Je n'ai pas trouvé" in answer
