from __future__ import annotations

from typing import Any

from app.models.schemas import (
    ChartDataRequest,
    ChatRequest,
    ChatResponse,
    CompareByYearRequest,
    DatasetRequest,
    FollowupRequest,
    QueryRowsRequest,
    SearchDatasetsRequest,
    SummarizeDatasetRequest,
)
from app.services.nlp import detect_intent, detect_language, extract_search_query, extract_years
from app.services.tools import DATASET_INVESTMENT_SLUG, ToolService


class ChatService:
    def __init__(self, tools: ToolService) -> None:
        self.tools = tools

    async def handle(self, payload: ChatRequest) -> ChatResponse:
        message = payload.message.strip()
        language = payload.language or detect_language(message)
        intent = detect_intent(message)
        traces = []
        data: dict[str, Any] = {}
        selected_dataset = payload.context.get("dataset")

        if intent == "compare":
            years = extract_years(message)
            request = CompareByYearRequest(
                dataset_id_or_slug=selected_dataset or DATASET_INVESTMENT_SLUG,
                year_field=payload.context.get("year_field", "annee"),
                value_field=payload.context.get(
                    "value_field",
                    "taux_dinvestissements_percent_du_pib",
                ),
                start_year=years[0],
                end_year=years[1],
            )
            envelope = await self.tools.compare_indicator_by_year(request)
            traces.append(envelope.trace)
            data = envelope.data
            answer = self._compare_answer(data, language)
            followup_context = "compare"
        elif intent == "schema":
            dataset = selected_dataset or DATASET_INVESTMENT_SLUG
            envelope = await self.tools.get_dataset_schema(DatasetRequest(dataset_id_or_slug=dataset))
            traces.append(envelope.trace)
            data = envelope.data
            answer = self._schema_answer(data, language)
            followup_context = "schema"
        elif intent == "rows":
            dataset = selected_dataset or DATASET_INVESTMENT_SLUG
            envelope = await self.tools.query_dataset_rows(QueryRowsRequest(dataset_id_or_slug=dataset, limit=8))
            traces.append(envelope.trace)
            data = envelope.data
            answer = self._rows_answer(data, language)
            followup_context = "rows"
        elif intent == "summary":
            dataset = selected_dataset or DATASET_INVESTMENT_SLUG
            envelope = await self.tools.summarize_public_dataset(
                SummarizeDatasetRequest(dataset_id_or_slug=dataset, language=language)
            )
            traces.append(envelope.trace)
            data = envelope.data
            answer = data.get("summary", "")
            followup_context = "summary"
        elif intent == "chart":
            dataset = selected_dataset or DATASET_INVESTMENT_SLUG
            envelope = await self.tools.build_chart_data(
                ChartDataRequest(
                    dataset_id_or_slug=dataset,
                    x_field=payload.context.get("x_field", "annee"),
                    y_field=payload.context.get(
                        "y_field",
                        "taux_dinvestissements_percent_du_pib",
                    ),
                    limit=30,
                )
            )
            traces.append(envelope.trace)
            data = envelope.data
            answer = (
                "J'ai préparé les données de graphique depuis data.gouv.ci."
                if language == "fr"
                else "I prepared chart data from data.gouv.ci."
            )
            followup_context = "details"
        else:
            query = extract_search_query(message, language)
            envelope = await self.tools.search_public_datasets(
                SearchDatasetsRequest(query=query, limit=8, language=language)
            )
            traces.append(envelope.trace)
            data = envelope.data
            first_result = (data.get("results") or [{}])[0]
            if isinstance(first_result, dict):
                selected_dataset = first_result.get("id") or first_result.get("slug")
                data["selected_dataset"] = selected_dataset
            answer = self._search_answer(data, language)
            followup_context = "search"

        followup = await self.tools.recommend_followup_questions(
            FollowupRequest(
                context_type=followup_context,
                dataset_id_or_slug=selected_dataset,
                language=language,
            )
        )
        traces.append(followup.trace)

        return ChatResponse(
            answer=answer,
            language=language,
            intent=intent,
            traces=traces,
            data=data,
            followups=followup.data.get("questions", []),
        )

    @staticmethod
    def _search_answer(data: dict[str, Any], language: str) -> str:
        shown = len(data.get("results", []))
        if language == "en":
            return f"I found {shown} public datasets from data.gouv.ci."
        return f"J'ai trouvé {shown} datasets publics sur data.gouv.ci."

    @staticmethod
    def _schema_answer(data: dict[str, Any], language: str) -> str:
        schema_count = len(data.get("schema", []))
        if language == "en":
            return f"This dataset exposes {schema_count} fields. I listed their keys, types and descriptions when available."
        return f"Ce dataset expose {schema_count} champs. J'ai listé les clés, types et descriptions disponibles."

    @staticmethod
    def _rows_answer(data: dict[str, Any], language: str) -> str:
        total = data.get("total", 0)
        shown = len(data.get("results", []))
        if language == "en":
            return f"I read {shown} real rows from this dataset. The dataset reports {total} rows in total."
        return f"J'ai lu {shown} lignes réelles depuis ce dataset. Le dataset indique {total} lignes au total."

    @staticmethod
    def _compare_answer(data: dict[str, Any], language: str) -> str:
        values = data.get("values", [])
        absolute_change = data.get("absolute_change")
        percent_change = data.get("percent_change")
        if language == "en":
            direction = (
                "increased"
                if isinstance(absolute_change, int | float) and absolute_change >= 0
                else "decreased"
            )
            pct = f" ({percent_change:.2f}%)" if isinstance(percent_change, int | float) else ""
            interpretation = f"The indicator {direction} by {absolute_change}{pct} over the selected period."
        else:
            direction = "augmente" if isinstance(absolute_change, int | float) and absolute_change >= 0 else "diminue"
            pct = f" ({percent_change:.2f}%)" if isinstance(percent_change, int | float) else ""
            interpretation = f"L'indicateur {direction} de {absolute_change}{pct} sur la période."
        if language == "en":
            return f"I compared {len(values)} yearly values from data.gouv.ci. {interpretation}"
        return f"J'ai comparé {len(values)} valeurs annuelles depuis data.gouv.ci. {interpretation}"
