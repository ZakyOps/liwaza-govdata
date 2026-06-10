# Clean Code Review

## Objectif

Cette note documente les principes de Clean Code appliques au projet Liwaza GovData apres audit du code existant.

Document de reference lu:

- `/Users/zakaria/Documents/Odoo/19.0/docs/clean_code.pdf`
- `/Users/zakaria/Documents/Odoo/19.0/docs/clean.pdf`

## Principes appliques

- Responsabilite unique: `ChatService` orchestre la conversation, tandis que `app/services/nlp.py` gere la detection de langue, l'intention, les annees et la requete de recherche.
- Noms explicites: les constantes `DEFAULT_YEAR_RANGE`, `TOPIC_ALIASES`, `SEARCH_COMMAND_WORDS` et `SEARCH_FILLER_WORDS` decrivent clairement leur role.
- Fonctions courtes: les traitements NLP sont decomposes en petites fonctions testables.
- Principe de moindre surprise: les resultats sont filtres pour rester dans le perimetre data.gouv.ci / Cote d'Ivoire, sans ajouter un wording inutile dans l'interface.
- Erreurs lisibles: le frontend transforme une erreur reseau technique en message utilisateur clair.
- Tests proches du comportement: les tests couvrent la detection de langue, l'extraction de requete et les reponses de base.
- Pas de donnees simulees pour le coeur metier: les outils MCP continuent d'appeler l'API reelle data.gouv.ci.

## Changements effectues

- Extraction des fonctions de langue/intention/recherche depuis `ChatService` vers `app/services/nlp.py`.
- Suppression d'un import inutilise apres refactor.
- Mise a jour des tests pour cibler directement le module NLP.
- Ajout d'un filtre backend contre les datasets federes hors perimetre.
- Conservation de l'orchestration MCP dans le backend, sans logique metier dans le frontend.

## Points a surveiller

- La detection de langue utilise Lingua avec un fallback lexical pour les messages courts ou ambigus.
- Les intentions restent volontairement simples pour le test technique; une evolution naturelle serait un routeur LLM avec validation stricte des outils.
- Le projet n'est pas encore initialise comme depot Git dans ce dossier local.

## Verification attendue

- `ruff check app tests`
- `pytest`
- `npm run build`
- Test manuel du frontend avec des questions en francais et en anglais.
