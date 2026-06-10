from __future__ import annotations

import time
import unicodedata
from typing import Any

from app.core.config import get_settings
from app.models.schemas import (
    ChartDataRequest,
    CompareByYearRequest,
    DatasetRequest,
    FieldValuesRequest,
    FollowupRequest,
    NumericMetricsRequest,
    QueryRowsRequest,
    SearchDatasetsRequest,
    SummarizeDatasetRequest,
    ToolEnvelope,
    ToolTrace,
)
from app.services.datafair import DataFairClient, DataFairError


DATASET_INVESTMENT_SLUG = (
    "evolution-du-taux-dinvestissement-percent-du-pib-et-de-la-formation-brute-de-capital-fixe-"
    "de-la-cote-divoire-entre-1960-et-2023"
)

FOREIGN_DATASET_MARKERS = [
    "data.gouv.fr",
    "situés en france",
    "situes en france",
    "situé en france",
    "situe en france",
    "ministère de l'éducation nationale et de la jeunesse",
    "ministere de l'education nationale et de la jeunesse",
    "source : ramsese",
]


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "search_public_datasets",
        "description": "Search public datasets on data.gouv.ci by keyword.",
        "input_schema": {"query": "string", "limit": "integer", "language": "fr|en"},
    },
    {
        "name": "get_dataset_details",
        "description": "Read detailed metadata for a public dataset.",
        "input_schema": {"dataset_id_or_slug": "string"},
    },
    {
        "name": "get_dataset_schema",
        "description": "List fields, types and descriptions for a dataset.",
        "input_schema": {"dataset_id_or_slug": "string"},
    },
    {
        "name": "query_dataset_rows",
        "description": "Read real rows from a public dataset.",
        "input_schema": {"dataset_id_or_slug": "string", "limit": "integer"},
    },
    {
        "name": "get_field_values",
        "description": "List distinct values for a dataset field.",
        "input_schema": {"dataset_id_or_slug": "string", "field": "string", "limit": "integer"},
    },
    {
        "name": "get_numeric_metrics",
        "description": "Compute simple metrics for a numeric field.",
        "input_schema": {"dataset_id_or_slug": "string", "field": "string"},
    },
    {
        "name": "compare_indicator_by_year",
        "description": "Compare a numeric indicator over a year range.",
        "input_schema": {
            "dataset_id_or_slug": "string",
            "year_field": "string",
            "value_field": "string",
            "start_year": "integer",
            "end_year": "integer",
        },
    },
    {
        "name": "summarize_public_dataset",
        "description": "Summarize a public dataset from real metadata and sample rows.",
        "input_schema": {"dataset_id_or_slug": "string", "language": "fr|en"},
    },
    {
        "name": "assess_dataset_quality",
        "description": "Score dataset documentation and usability quality.",
        "input_schema": {"dataset_id_or_slug": "string"},
    },
    {
        "name": "build_chart_data",
        "description": "Prepare chart-ready points from real dataset rows.",
        "input_schema": {
            "dataset_id_or_slug": "string",
            "x_field": "string",
            "y_field": "string",
            "limit": "integer",
        },
    },
    {
        "name": "recommend_followup_questions",
        "description": "Recommend useful follow-up questions for the user.",
        "input_schema": {"context_type": "string", "dataset_id_or_slug": "string?", "language": "fr|en"},
    },
]


class ToolService:
    def __init__(self) -> None:
        self.client = DataFairClient()
        self.settings = get_settings()

    def _trace(
        self,
        tool: str,
        start: float,
        status: str = "success",
        endpoint: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> ToolTrace:
        return ToolTrace(
            tool=tool,
            status=status,  # type: ignore[arg-type]
            duration_ms=int((time.perf_counter() - start) * 1000),
            endpoint=endpoint,
            params=params or {},
        )

    def _envelope(
        self,
        tool: str,
        start: float,
        data: dict[str, Any],
        endpoint: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> ToolEnvelope:
        return ToolEnvelope(
            status="success",
            tool=tool,
            trace=self._trace(tool, start, "success", endpoint, params),
            data=data,
        )

    @staticmethod
    def _dataset_summary(dataset: dict[str, Any]) -> dict[str, Any]:
        license_data = dataset.get("license") or {}
        return {
            "id": dataset.get("id"),
            "slug": dataset.get("slug"),
            "title": dataset.get("title"),
            "description": dataset.get("description"),
            "origin": dataset.get("origin"),
            "updatedAt": dataset.get("updatedAt"),
            "createdAt": dataset.get("createdAt"),
            "count": dataset.get("count"),
            "license": license_data.get("title") if isinstance(license_data, dict) else license_data,
            "page": dataset.get("page"),
            "href": dataset.get("href"),
            "topics": [topic.get("title") for topic in dataset.get("topics", []) if isinstance(topic, dict)],
        }

    @staticmethod
    def _is_cote_divoire_dataset(dataset: dict[str, Any]) -> bool:
        searchable_text = " ".join(
            str(dataset.get(field) or "")
            for field in ["id", "slug", "title", "description", "origin", "page", "href"]
        ).lower()
        return not any(marker in searchable_text for marker in FOREIGN_DATASET_MARKERS)

    async def search_public_datasets(self, payload: SearchDatasetsRequest) -> ToolEnvelope:
        start = time.perf_counter()
        fetch_limit = max(payload.limit * 5, 30)
        raw = await self.client.list_datasets(payload.query, fetch_limit)
        ivoirian_results = [
            self._dataset_summary(item)
            for item in raw.get("results", [])
            if self._is_cote_divoire_dataset(item)
        ][: payload.limit]
        return self._envelope(
            "search_public_datasets",
            start,
            {
                "count": len(ivoirian_results),
                "source_count": raw.get("count", len(ivoirian_results)),
                "results": ivoirian_results,
                "country_filter": "CI",
            },
            "GET /datasets",
            {**payload.model_dump(), "country_filter": "CI", "fetched": fetch_limit},
        )

    async def get_dataset_details(self, payload: DatasetRequest) -> ToolEnvelope:
        start = time.perf_counter()
        dataset = await self.client.get_dataset(payload.dataset_id_or_slug)
        data = self._dataset_summary(dataset)
        data.update(
            {
                "schema_preview": dataset.get("schema", [])[:12],
                "files": (dataset.get("storage") or {}).get("dataFiles", []),
                "public": dataset.get("public"),
                "visibility": dataset.get("visibility"),
            }
        )
        return self._envelope(
            "get_dataset_details",
            start,
            data,
            "GET /datasets/{dataset}",
            payload.model_dump(),
        )

    async def get_dataset_schema(self, payload: DatasetRequest) -> ToolEnvelope:
        start = time.perf_counter()
        dataset = await self.client.get_dataset(payload.dataset_id_or_slug)
        schema = []
        for field in dataset.get("schema", []):
            schema.append(
                {
                    "key": field.get("key"),
                    "type": field.get("type"),
                    "title": field.get("title") or field.get("x-originalName") or field.get("key"),
                    "description": field.get("description"),
                }
            )
        return self._envelope(
            "get_dataset_schema",
            start,
            {"dataset": self._dataset_summary(dataset), "schema": schema},
            "GET /datasets/{dataset}",
            payload.model_dump(),
        )

    async def query_dataset_rows(self, payload: QueryRowsRequest) -> ToolEnvelope:
        start = time.perf_counter()
        raw = await self.client.get_lines(
            payload.dataset_id_or_slug,
            payload.limit,
            payload.sort,
            payload.qs,
        )
        return self._envelope(
            "query_dataset_rows",
            start,
            {"total": raw.get("total"), "next": raw.get("next"), "results": raw.get("results", [])},
            "GET /datasets/{dataset}/lines",
            payload.model_dump(),
        )

    async def get_field_values(self, payload: FieldValuesRequest) -> ToolEnvelope:
        start = time.perf_counter()
        raw = await self.client.get_values(payload.dataset_id_or_slug, payload.field, payload.limit)
        return self._envelope(
            "get_field_values",
            start,
            {"field": payload.field, "values": raw},
            "GET /datasets/{dataset}/values/{field}",
            payload.model_dump(),
        )

    async def get_numeric_metrics(self, payload: NumericMetricsRequest) -> ToolEnvelope:
        start = time.perf_counter()
        metrics: dict[str, Any] = {}
        for metric in ["min", "max", "avg", "sum"]:
            try:
                metrics[metric] = await self.client.get_metric(payload.dataset_id_or_slug, payload.field, metric)
            except DataFairError as exc:
                metrics[metric] = {"error": str(exc)}
        return self._envelope(
            "get_numeric_metrics",
            start,
            {"field": payload.field, "metrics": metrics},
            "GET /datasets/{dataset}/metric_agg",
            payload.model_dump(),
        )

    async def compare_indicator_by_year(self, payload: CompareByYearRequest) -> ToolEnvelope:
        start = time.perf_counter()
        auto_fields = payload.year_field == "__auto__" or payload.value_field == "__auto__"
        raw = await self.client.get_lines(
            payload.dataset_id_or_slug,
            100,
            None if auto_fields else f"-{payload.year_field}",
            None,
        )
        rows = raw.get("results", [])
        year_field = payload.year_field
        value_field = payload.value_field
        if auto_fields:
            year_field, value_field = self._infer_comparison_fields(rows, year_field, value_field)

        values = []
        for row in rows:
            year = row.get(year_field)
            value = row.get(value_field)
            if isinstance(year, int) and payload.start_year <= year <= payload.end_year and isinstance(value, int | float):
                values.append({"year": year, "value": value})
        values = sorted(values, key=lambda item: item["year"])
        first = values[0]["value"] if values else None
        last = values[-1]["value"] if values else None
        absolute_change = last - first if isinstance(first, int | float) and isinstance(last, int | float) else None
        percent_change = (
            (absolute_change / first) * 100
            if isinstance(absolute_change, int | float) and isinstance(first, int | float) and first != 0
            else None
        )
        return self._envelope(
            "compare_indicator_by_year",
            start,
            {
                "values": values,
                "absolute_change": absolute_change,
                "percent_change": percent_change,
                "interpretation": self._comparison_text(values, absolute_change, percent_change),
                "year_field": year_field,
                "value_field": value_field,
            },
            "GET /datasets/{dataset}/lines",
            {**payload.model_dump(), "resolved_year_field": year_field, "resolved_value_field": value_field},
        )

    async def summarize_public_dataset(self, payload: SummarizeDatasetRequest) -> ToolEnvelope:
        start = time.perf_counter()
        dataset = await self.client.get_dataset(payload.dataset_id_or_slug)
        rows = await self.client.get_lines(payload.dataset_id_or_slug, 5)
        schema = dataset.get("schema", [])
        title = dataset.get("title") or payload.dataset_id_or_slug
        count = dataset.get("count")
        columns = [field.get("key") for field in schema[:8]]
        if payload.language == "en":
            summary = f"{title} contains {count or 'an unknown number of'} rows. Key fields include {', '.join(columns)}."
        else:
            summary = f"{title} contient {count or 'un nombre non precise de'} lignes. Les champs clés incluent {', '.join(columns)}."
        return self._envelope(
            "summarize_public_dataset",
            start,
            {
                "dataset": self._dataset_summary(dataset),
                "summary": summary,
                "sample_rows": rows.get("results", []),
                "limitations": [
                    "La synthèse dépend des métadonnées publiées.",
                    "Les premières lignes ne représentent pas forcément tout le dataset.",
                ],
            },
            "GET /datasets/{dataset} + GET /datasets/{dataset}/lines",
            payload.model_dump(),
        )

    async def assess_dataset_quality(self, payload: DatasetRequest) -> ToolEnvelope:
        start = time.perf_counter()
        dataset = await self.client.get_dataset(payload.dataset_id_or_slug)
        score = 0
        checks = {
            "has_description": bool(dataset.get("description")),
            "has_schema": bool(dataset.get("schema")),
            "has_license": bool(dataset.get("license")),
            "has_recent_update": bool(dataset.get("updatedAt")),
            "has_rows": bool(dataset.get("count")),
        }
        score += 25 if checks["has_description"] else 0
        score += 25 if checks["has_schema"] else 0
        score += 20 if checks["has_license"] else 0
        score += 15 if checks["has_recent_update"] else 0
        score += 15 if checks["has_rows"] else 0
        return self._envelope(
            "assess_dataset_quality",
            start,
            {"score": score, "checks": checks, "dataset": self._dataset_summary(dataset)},
            "GET /datasets/{dataset}",
            payload.model_dump(),
        )

    async def build_chart_data(self, payload: ChartDataRequest) -> ToolEnvelope:
        start = time.perf_counter()
        raw = await self.client.get_lines(payload.dataset_id_or_slug, payload.limit, payload.x_field)
        points = []
        for row in raw.get("results", []):
            if payload.x_field in row and payload.y_field in row:
                points.append({"x": row[payload.x_field], "y": row[payload.y_field]})
        return self._envelope(
            "build_chart_data",
            start,
            {
                "points": points,
                "chart_type": "line" if points and isinstance(points[0]["x"], int) else "bar",
                "x_field": payload.x_field,
                "y_field": payload.y_field,
            },
            "GET /datasets/{dataset}/lines",
            payload.model_dump(),
        )

    async def recommend_followup_questions(self, payload: FollowupRequest) -> ToolEnvelope:
        start = time.perf_counter()
        fr = payload.language == "fr"
        has_dataset = bool(payload.dataset_id_or_slug)
        questions_by_context = {
            "search": [
                "Affiche le schéma du dataset sélectionné.",
                "Résume le dataset sélectionné.",
                "Montre-moi quelques lignes réelles du dataset sélectionné.",
            ],
            "details": [
                "Évalue la qualité de ce dataset.",
                "Montre les valeurs disponibles d'un champ.",
                "Prépare les données pour un graphique.",
            ],
            "generic": [
                "Trouve les datasets liés à l'éducation.",
                "Cherche les données économiques récentes.",
                "Compare un indicateur par année.",
            ],
        }
        english_generic = [
            "Show the schema of the selected dataset.",
            "Show sample rows from the selected dataset.",
            "Summarize the selected dataset.",
        ]
        questions = questions_by_context.get(payload.context_type, questions_by_context["generic"])
        if not fr:
            questions = english_generic
        if not has_dataset and payload.context_type != "generic":
            questions = questions_by_context["generic"] if fr else [
                "Search datasets about education.",
                "Search economic datasets.",
                "Compare a yearly indicator.",
            ]
        return self._envelope(
            "recommend_followup_questions",
            start,
            {"questions": questions},
            None,
            payload.model_dump(),
        )

    @staticmethod
    def _comparison_text(
        values: list[dict[str, Any]],
        absolute_change: float | int | None,
        percent_change: float | int | None,
    ) -> str:
        if not values:
            return "Aucune valeur exploitable n'a ete trouvee pour cette periode."
        direction = "augmente" if absolute_change and absolute_change > 0 else "diminue"
        pct = f" ({percent_change:.2f}%)" if isinstance(percent_change, int | float) else ""
        return f"L'indicateur {direction} de {absolute_change}{pct} sur la periode."

    @classmethod
    def _infer_comparison_fields(
        cls,
        rows: list[dict[str, Any]],
        requested_year_field: str,
        requested_value_field: str,
    ) -> tuple[str, str]:
        if not rows:
            return requested_year_field, requested_value_field

        keys = [key for row in rows for key in row.keys()]
        unique_keys = list(dict.fromkeys(keys))
        year_field = (
            requested_year_field
            if requested_year_field != "__auto__"
            else cls._infer_year_field(rows, unique_keys)
        )
        value_field = (
            requested_value_field
            if requested_value_field != "__auto__"
            else cls._infer_value_field(rows, unique_keys, year_field)
        )
        return year_field, value_field

    @classmethod
    def _infer_year_field(cls, rows: list[dict[str, Any]], keys: list[str]) -> str:
        preferred = ["annee", "année", "year", "annees", "années"]
        for key in keys:
            if cls._normalize_key(key) in preferred and cls._has_year_values(rows, key):
                return key
        for key in keys:
            normalized = cls._normalize_key(key)
            if ("annee" in normalized or "year" in normalized) and cls._has_year_values(rows, key):
                return key
        for key in keys:
            if cls._has_year_values(rows, key):
                return key
        return "annee"

    @classmethod
    def _infer_value_field(cls, rows: list[dict[str, Any]], keys: list[str], year_field: str) -> str:
        ignored = {"_id", "_i", "_rand", "_score", year_field}
        candidates = []
        for key in keys:
            if key in ignored:
                continue
            values = [row.get(key) for row in rows]
            numeric_values = [value for value in values if isinstance(value, int | float)]
            if not numeric_values:
                continue
            non_zero_count = sum(1 for value in numeric_values if value != 0)
            candidates.append((len(numeric_values), non_zero_count, key))
        if not candidates:
            return "taux_dinvestissements_percent_du_pib"
        candidates.sort(key=lambda item: (item[1], item[0]), reverse=True)
        return candidates[0][2]

    @staticmethod
    def _has_year_values(rows: list[dict[str, Any]], key: str) -> bool:
        return any(isinstance(row.get(key), int) and 1900 <= row[key] <= 2100 for row in rows)

    @staticmethod
    def _normalize_key(key: str) -> str:
        normalized = unicodedata.normalize("NFKD", key.lower()).encode("ascii", "ignore").decode("ascii")
        return normalized.replace(" ", "_").replace("-", "_")


def get_tool_service() -> ToolService:
    return ToolService()
