from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


Language = Literal["fr", "en"]


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ToolTrace(BaseModel):
    tool: str
    status: Literal["success", "error", "partial"]
    duration_ms: int
    source: str = "data.gouv.ci"
    endpoint: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ToolEnvelope(BaseModel):
    status: Literal["success", "error", "partial"]
    tool: str
    trace: ToolTrace
    data: dict[str, Any]


class SearchDatasetsRequest(BaseModel):
    query: str = Field(min_length=1, max_length=120)
    limit: int = Field(default=8, ge=1, le=30)
    language: Language = "fr"


class DatasetRequest(BaseModel):
    dataset_id_or_slug: str = Field(min_length=1, max_length=220)


class QueryRowsRequest(DatasetRequest):
    limit: int = Field(default=10, ge=1, le=50)
    sort: str | None = Field(default=None, max_length=80)
    qs: str | None = Field(default=None, max_length=240)


class FieldValuesRequest(DatasetRequest):
    field: str = Field(min_length=1, max_length=120)
    limit: int = Field(default=20, ge=1, le=50)


class NumericMetricsRequest(DatasetRequest):
    field: str = Field(min_length=1, max_length=120)


class CompareByYearRequest(DatasetRequest):
    year_field: str = Field(default="annee", min_length=1, max_length=120)
    value_field: str = Field(min_length=1, max_length=160)
    start_year: int = Field(ge=1900, le=2100)
    end_year: int = Field(ge=1900, le=2100)

    @field_validator("end_year")
    @classmethod
    def validate_year_range(cls, end_year: int, info):
        start_year = info.data.get("start_year")
        if start_year and end_year < start_year:
            raise ValueError("end_year must be greater than or equal to start_year")
        return end_year


class SummarizeDatasetRequest(DatasetRequest):
    language: Language = "fr"


class ChartDataRequest(DatasetRequest):
    x_field: str = Field(min_length=1, max_length=120)
    y_field: str = Field(min_length=1, max_length=160)
    limit: int = Field(default=25, ge=2, le=100)


class FollowupRequest(BaseModel):
    context_type: Literal["search", "details", "schema", "rows", "compare", "summary", "generic"] = "generic"
    dataset_id_or_slug: str | None = Field(default=None, max_length=220)
    language: Language = "fr"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: Language | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str
    language: Language
    intent: str
    traces: list[ToolTrace]
    data: dict[str, Any] = Field(default_factory=dict)
    followups: list[str] = Field(default_factory=list)
