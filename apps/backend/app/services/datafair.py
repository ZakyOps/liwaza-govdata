from typing import Any

import httpx

from app.core.config import get_settings


class DataFairError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class DataFairClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.datafair_base_url.rstrip("/")

    async def request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = httpx.Timeout(self.settings.request_timeout_seconds)
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise DataFairError(
                f"data.gouv.ci returned HTTP {exc.response.status_code}",
                exc.response.status_code,
            ) from exc
        except httpx.TimeoutException as exc:
            raise DataFairError("data.gouv.ci request timed out") from exc
        except httpx.HTTPError as exc:
            raise DataFairError(f"data.gouv.ci request failed: {exc}") from exc
        except ValueError as exc:
            raise DataFairError("data.gouv.ci returned invalid JSON") from exc

    async def list_datasets(self, query: str, limit: int) -> dict[str, Any]:
        return await self.request("datasets", {"q": query, "size": limit})

    async def get_dataset(self, dataset_id_or_slug: str) -> dict[str, Any]:
        return await self.request(f"datasets/{dataset_id_or_slug}")

    async def get_lines(
        self,
        dataset_id_or_slug: str,
        limit: int,
        sort: str | None = None,
        qs: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"size": limit}
        if sort:
            params["sort"] = sort
        if qs:
            params["qs"] = qs
        return await self.request(f"datasets/{dataset_id_or_slug}/lines", params)

    async def get_values(self, dataset_id_or_slug: str, field: str, limit: int) -> dict[str, Any]:
        return await self.request(f"datasets/{dataset_id_or_slug}/values/{field}", {"size": limit})

    async def get_metric(self, dataset_id_or_slug: str, field: str, metric: str) -> dict[str, Any]:
        return await self.request(
            f"datasets/{dataset_id_or_slug}/metric_agg",
            {"field": field, "metric": metric},
        )
