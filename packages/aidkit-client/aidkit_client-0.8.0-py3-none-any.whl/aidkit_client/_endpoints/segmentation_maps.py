from typing import List

from aidkit_client._endpoints.models import SegmentationMapResponse
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.exceptions import ResourceWithIdNotFoundError


class SegmentationMapAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def create(
        self,
        observation_id: int,
        segmentation_map_data: List[List[int]],
        class_names: List[str],
    ) -> SegmentationMapResponse:
        return SegmentationMapResponse(
            **(
                await self.api.post_json(
                    path=f"/observation/{observation_id}/segmentation_map",
                    body={
                        "class_names": class_names,
                        "segmentation_map_data": segmentation_map_data,
                    },
                )
            ).body_dict_or_error(
                f"Failed to create segmentation map for observation {observation_id}."
            )
        )

    async def get_by_observation_id(self, observation_id: int) -> SegmentationMapResponse:
        result = await self.api.get(
            path=f"observation/{observation_id}/segmentation_map", parameters=None
        )
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(
                f"Segmentation map for observation with id {observation_id} not found"
            )
        return SegmentationMapResponse(
            **result.body_dict_or_error(
                f"Error fetching Segmentation map for observation with id {observation_id}."
            )
        )
