# Benchmark des APIs publiques pour le test Liwaza

Date du benchmark : 2026-06-08  
Contexte candidat : Abidjan / Côte d'Ivoire

## Objectif

Choisir le service public le plus adapté pour construire une plateforme eGov AI-native avec :

- React comme client MCP ;
- Python/FastAPI comme serveur MCP ;
- au moins 5 outils MCP utiles ;
- exécution réelle des outils ;
- API publique réellement appelable pendant la démo.

## Résumé exécutif

Recommandation principale : **data.gouv.ci via l'API Data Fair publique**.

Pourquoi : c'est l'option la plus sûre pour livrer dans 12-15 heures. L'API répond publiquement, retourne du JSON, permet de rechercher des datasets, lire des schémas, lire des lignes, faire des agrégations et construire des réponses conversationnelles vérifiables. Elle colle très bien à l'obligation du test : les reviewers peuvent inspecter le trafic et constater que les résultats viennent d'appels réels.

Option ambitieuse mais risquée : **FNE / DGI Côte d'Ivoire**.

Pourquoi : le domaine métier est plus fort et plus proche des exemples du test, mais l'accès opérationnel nécessite une validation DGI et une clé API. Sans clé, on risque de se retrouver avec une belle architecture mais une démonstration non exécutable de bout en bout.

## Options étudiées

| Option | API exploitable | Accès | Valeur produit | Risque livraison | Verdict |
|---|---:|---|---:|---:|---|
| data.gouv.ci / Data Fair | Oui | Public en lecture | Moyen à fort | Faible | Choix recommandé |
| FNE / DGI CI | Oui, documentée | Clé + validation DGI | Très fort | Élevé | À mentionner comme future intégration |
| GUCE CI | Portail transactionnel, API métier non clairement ouverte | Accès probablement contrôlé | Fort | Élevé | Pas idéal pour ce test |
| DGI Cameroun | Documentation métier disponible, API moins évidente | Accès contrôlé/probable | Fort | Élevé | Pertinent seulement pour Yaoundé |
| Open Data Cameroon | Portail open data possible | Public selon source | Moyen | Moyen | Alternative si contexte Yaoundé |

## Tests techniques rapides

Tests non intrusifs réalisés avec `curl` :

| Cible | Résultat | Temps |
|---|---:|---:|
| `https://data.gouv.ci/datasets` | HTTP 200 | 0.98 s |
| `https://data.gouv.ci/data-fair/api/v1/datasets` | HTTP 200 | 1.41 s |
| `https://data.gouv.ci/data-fair/api/v1/datasets/{slug}/lines?size=1` | HTTP 200 | 0.50 s |
| `https://www.dgi.gouv.ci/assets/documents/FNE-procedureapi.pdf` | HTTP 200 | 0.28 s |
| `https://www.gucecotedivoire.ci/` | HTTP 200 | 2.29 s |
| `http://54.247.95.108/ws` | HTTP 404 sur racine | 0.24 s |

Interprétation : la racine du serveur de test FNE ne prouve pas que les endpoints métier soient indisponibles ; la documentation indique des chemins POST spécifiques et une authentification Bearer. En revanche, cela confirme que FNE n'est pas une intégration publique immédiate sans credentials.

## API recommandée : data.gouv.ci / Data Fair

Base URL :

```text
https://data.gouv.ci/data-fair/api/v1
```

Endpoints utiles :

```text
GET /datasets
GET /datasets/{datasetIdOrSlug}
GET /datasets/{datasetIdOrSlug}/lines
GET /datasets/{datasetIdOrSlug}/values/{field}
GET /datasets/{datasetIdOrSlug}/metric_agg
```

Exemple vérifié :

```text
GET https://data.gouv.ci/data-fair/api/v1/datasets/evolution-du-taux-dinvestissement-percent-du-pib-et-de-la-formation-brute-de-capital-fixe-de-la-cote-divoire-entre-1960-et-2023/lines?size=2
```

Réponse observée : JSON avec `total`, `next` et `results`. Les résultats contiennent notamment `annee`, `taux_dinvestissements_percent_du_pib` et `formation_brute_de_capital_fixe_investissements_milliards`.

## Outils MCP possibles

Avec data.gouv.ci, on peut exposer au moins 5 outils réels :

1. `search_public_datasets`
   - Recherche des jeux de données par mot-clé, thème ou producteur.
   - Exemple utilisateur : "Trouve les données fiscales disponibles en Côte d'Ivoire."

2. `get_dataset_schema`
   - Retourne les colonnes, types, source, licence, date de mise à jour.
   - Utile pour expliquer à l'utilisateur ce que l'IA peut calculer.

3. `query_dataset_rows`
   - Lit des lignes filtrées et paginées.
   - Exemple : "Montre-moi les recettes fiscales depuis 2015."

4. `compare_indicators`
   - Compare plusieurs années ou plusieurs indicateurs dans un dataset.
   - Exemple : "Compare inflation et investissement entre 2018 et 2023."

5. `summarize_public_dataset`
   - Combine métadonnées + lignes + agrégations pour produire une synthèse en français ou anglais.
   - Exemple : "Résume l'évolution du budget de l'État."

Outils bonus :

- `download_dataset_csv`
- `get_dataset_sources`
- `build_chart_data`
- `answer_open_data_question`

## Score détaillé

Notation sur 5.

| Critère | data.gouv.ci | FNE/DGI CI | GUCE CI |
|---|---:|---:|---:|
| API publique testable maintenant | 5 | 2 | 2 |
| Documentation exploitable | 4 | 4 | 2 |
| Authentification simple | 5 | 2 | 2 |
| Richesse métier | 3 | 5 | 4 |
| Démo vérifiable par reviewer | 5 | 3 | 2 |
| Possibilité de 5 outils MCP | 5 | 4 | 3 |
| Risque de blocage | 5 | 2 | 2 |
| Alignement eGov | 4 | 5 | 5 |
| Total | **36/40** | **27/40** | **22/40** |

## Décision proposée

Construire la version test autour de **data.gouv.ci** et présenter FNE/DGI comme évolution prioritaire.

Positionnement produit :

> Un assistant eGov bilingue qui permet aux citoyens, entreprises, journalistes et décideurs d'interroger les données publiques ivoiriennes en langage naturel, avec des réponses structurées, sourcées et calculées depuis les APIs publiques.

Cette stratégie maximise les chances de livrer :

- une vraie exécution MCP ;
- un backend FastAPI propre ;
- un frontend conversationnel crédible ;
- une documentation solide ;
- une démo inspectable ;
- un raisonnement d'ingénieur défendable.

## Sources

- MCP : https://modelcontextprotocol.io/docs/getting-started/intro
- Portail data.gouv.ci : https://data.gouv.ci/datasets
- API Data Fair : https://data-fair.github.io/3/interoperate/api/
- FNE Côte d'Ivoire : https://www.fne.dgi.gouv.ci/facturation.php
- Guide API FNE : https://www.dgi.gouv.ci/assets/documents/FNE-procedureapi.pdf
- FAQ FNE : https://www.fne.dgi.gouv.ci/faq.php
- GUCE CI : https://www.gucecotedivoire.ci/
