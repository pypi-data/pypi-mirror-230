from typing import List

from aidkit_client._endpoints.constants import Constants
from aidkit_client._endpoints.models import (
    ListSubsetResponse,
    SubsetCreateRequest,
    SubsetResponse,
    SubsetUpdateRequest,
)
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.exceptions import ResourceWithIdNotFoundError


class SubsetAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def get(self, subset_id: int) -> SubsetResponse:
        result = await self.api.get(path=f"{Constants.SUBSETS_PATH}/{subset_id}", parameters=None)
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(f"Subset with id {subset_id} not found")
        return SubsetResponse(
            **result.body_dict_or_error(f"Error fetching Subset with id {subset_id}.")
        )

    async def get_all(self, dataset_id: int) -> List[SubsetResponse]:
        result = await self.api.get(
            path=f"{Constants.SUBSETS_PATH}", parameters={"dataset_id": dataset_id}
        )
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(f"Dataset with id {dataset_id} not found")
        return ListSubsetResponse(
            **result.body_dict_or_error(
                f"Error fetching Subsets from Dataset with id {dataset_id}."
            )
        ).subsets

    async def create(
        self, subset_name: str, dataset_id: int, observation_ids: List[int]
    ) -> SubsetResponse:
        body = SubsetCreateRequest(
            name=subset_name, dataset_id=dataset_id, observation_ids=observation_ids
        ).dict()
        return SubsetResponse(
            **(
                await self.api.post_json(
                    path=f"{Constants.SUBSETS_PATH}",
                    parameters=None,
                    body=body,
                )
            ).body_dict_or_error(f"Failed to create subset '{subset_name}'.")
        )

    async def update(self, subset_id: int, observation_ids: List[int]) -> SubsetResponse:
        body = SubsetUpdateRequest(observation_ids=observation_ids).dict()
        return SubsetResponse(
            **(
                await self.api.patch(
                    path=f"{Constants.SUBSETS_PATH}/{subset_id}",
                    parameters=None,
                    body=body,
                )
            ).body_dict_or_error(
                f"Failed to update subset '{subset_id}'."  # noqa: S608
            )
        )

    async def delete(self, subset_id: int) -> None:
        await self.api.delete(path=f"{Constants.SUBSETS_PATH}/{subset_id}")
