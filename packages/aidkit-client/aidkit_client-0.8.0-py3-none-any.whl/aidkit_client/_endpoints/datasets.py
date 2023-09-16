import json
from typing import List

from aidkit_client._endpoints.constants import Constants
from aidkit_client._endpoints.models import (
    DatasetResponse,
    DatasetUploadRequest,
    ListDatasetResponse,
    ObservationType,
)
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.exceptions import ResourceWithIdNotFoundError


class DatasetAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def get(self, dataset_id: int) -> DatasetResponse:
        result = await self.api.get(path=f"{Constants.DATASETS_PATH}/{dataset_id}", parameters=None)
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(f"Dataset with id {dataset_id} not found")
        return DatasetResponse(
            **result.body_dict_or_error(f"Error fetching Dataset with id {dataset_id}.")
        )

    async def get_all(self) -> List[DatasetResponse]:
        result = await self.api.get(path=Constants.DATASETS_PATH, parameters=None)
        return ListDatasetResponse(
            **result.body_dict_or_error("Failed to retrieve Datasets.")
        ).items

    async def create(self, dataset_name: str, dataset_type: ObservationType) -> DatasetResponse:
        # needs to go through json to convert the enums, otherwise httpx will throw an error
        body = json.loads(DatasetUploadRequest(name=dataset_name, type=dataset_type).json())
        return DatasetResponse(
            **(
                await self.api.post_json(
                    path=f"{Constants.DATASETS_PATH}",
                    parameters=None,
                    body=body,
                )
            ).body_dict_or_error(f"Failed to create dataset '{dataset_name}'.")
        )

    async def delete(self, dataset_id: int) -> None:
        await self.api.delete(path=f"{Constants.DATASETS_PATH}/{dataset_id}")
