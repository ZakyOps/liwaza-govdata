from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.security import require_api_key
from app.models.schemas import (
    ChartDataRequest,
    ChatRequest,
    ChatResponse,
    CompareByYearRequest,
    DatasetRequest,
    FieldValuesRequest,
    FollowupRequest,
    NumericMetricsRequest,
    QueryRowsRequest,
    SearchDatasetsRequest,
    SummarizeDatasetRequest,
    ToolEnvelope,
)
from app.services.chat import ChatService
from app.services.tools import TOOL_DEFINITIONS, ToolService, get_tool_service

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"status": "ready", "datafair_base_url": settings.datafair_base_url}


@router.get("/version")
async def version(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"name": settings.app_name, "version": settings.app_version, "environment": settings.environment}


@router.get("/api/public-config")
async def public_config(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"appName": settings.app_name, "version": settings.app_version}


@router.get("/api/conversations/examples")
async def examples() -> dict[str, list[str]]:
    return {
        "fr": [
            "Trouve les datasets lies a l'education",
            "Compare les investissements entre 2020 et 2023",
            "Resume le dataset d'investissement",
            "Montre les colonnes disponibles",
        ],
        "en": [
            "Search public datasets about health",
            "Show sample rows",
            "Summarize the investment dataset",
            "Prepare chart data",
        ],
    }


@router.get("/mcp/tools")
async def list_tools() -> dict[str, list[dict]]:
    return {"tools": TOOL_DEFINITIONS}


@router.get("/mcp/capabilities")
async def capabilities() -> dict[str, object]:
    return {
        "name": "liwaza-govdata-mcp",
        "tools": True,
        "resources": True,
        "prompts": True,
        "real_api_execution": True,
        "source": "data.gouv.ci",
    }


@router.get("/mcp/resources")
async def resources() -> dict[str, list[dict[str, str]]]:
    return {
        "resources": [
            {"name": "data.gouv.ci datasets", "uri": "datafair://datasets"},
            {"name": "investment reference dataset", "uri": "datafair://datasets/investment"},
        ]
    }


@router.get("/mcp/prompts")
async def prompts() -> dict[str, list[dict[str, str]]]:
    return {
        "prompts": [
            {"name": "search_datasets", "description": "Find public datasets by topic."},
            {"name": "compare_indicator", "description": "Compare a yearly numeric indicator."},
            {"name": "summarize_dataset", "description": "Explain a dataset in plain language."},
        ]
    }


@router.post("/mcp/initialize")
async def initialize() -> dict[str, object]:
    return {
        "protocol": "mcp-http-pragmatic",
        "server": "liwaza-govdata-mcp",
        "tools": len(TOOL_DEFINITIONS),
    }


@router.post("/mcp/tools/search_public_datasets", dependencies=[Depends(require_api_key)])
async def search_public_datasets(
    payload: SearchDatasetsRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.search_public_datasets(payload)


@router.post("/mcp/tools/get_dataset_details", dependencies=[Depends(require_api_key)])
async def get_dataset_details(
    payload: DatasetRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.get_dataset_details(payload)


@router.post("/mcp/tools/get_dataset_schema", dependencies=[Depends(require_api_key)])
async def get_dataset_schema(
    payload: DatasetRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.get_dataset_schema(payload)


@router.post("/mcp/tools/query_dataset_rows", dependencies=[Depends(require_api_key)])
async def query_dataset_rows(
    payload: QueryRowsRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.query_dataset_rows(payload)


@router.post("/mcp/tools/get_field_values", dependencies=[Depends(require_api_key)])
async def get_field_values(
    payload: FieldValuesRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.get_field_values(payload)


@router.post("/mcp/tools/get_numeric_metrics", dependencies=[Depends(require_api_key)])
async def get_numeric_metrics(
    payload: NumericMetricsRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.get_numeric_metrics(payload)


@router.post("/mcp/tools/compare_indicator_by_year", dependencies=[Depends(require_api_key)])
async def compare_indicator_by_year(
    payload: CompareByYearRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.compare_indicator_by_year(payload)


@router.post("/mcp/tools/summarize_public_dataset", dependencies=[Depends(require_api_key)])
async def summarize_public_dataset(
    payload: SummarizeDatasetRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.summarize_public_dataset(payload)


@router.post("/mcp/tools/assess_dataset_quality", dependencies=[Depends(require_api_key)])
async def assess_dataset_quality(
    payload: DatasetRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.assess_dataset_quality(payload)


@router.post("/mcp/tools/build_chart_data", dependencies=[Depends(require_api_key)])
async def build_chart_data(
    payload: ChartDataRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.build_chart_data(payload)


@router.post("/mcp/tools/recommend_followup_questions", dependencies=[Depends(require_api_key)])
async def recommend_followup_questions(
    payload: FollowupRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ToolEnvelope:
    return await tools.recommend_followup_questions(payload)


@router.post("/api/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
async def chat(
    payload: ChatRequest,
    tools: ToolService = Depends(get_tool_service),
) -> ChatResponse:
    service = ChatService(tools)
    return await service.handle(payload)
