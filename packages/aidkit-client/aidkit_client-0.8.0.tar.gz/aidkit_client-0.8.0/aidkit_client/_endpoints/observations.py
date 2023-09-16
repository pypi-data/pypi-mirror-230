from typing import BinaryIO, List, Optional

from aidkit_client._endpoints.constants import Constants
from aidkit_client._endpoints.models import (
    ListObservationResponse,
    ObservationResponse,
    ObservationType,
)
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.exceptions import ResourceWithIdNotFoundError


class ObservationAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def create(
        self,
        dataset_id: int,
        observation_type: ObservationType,
        subset_ids: List[int],
        obs_name: str,
        obs_data: BinaryIO,
        odd_tags: Optional[List[str]],
    ) -> ObservationResponse:
        return ObservationResponse(
            **(
                await self.api.post_multipart_data(
                    f"observations?dataset_id={dataset_id}",
                    data={
                        "observation_type": observation_type.value,
                        "subset_ids": subset_ids,
                        "odd_tags": odd_tags,
                    },
                    files={"observation": (obs_name, obs_data)},
                )
            ).body_dict_or_error(f"Failed to create Observation {obs_name}.")
        )

    async def get_by_id(self, observation_id: int) -> ObservationResponse:
        result = await self.api.get(
            path=f"{Constants.OBSERVATIONS_PATH}/{observation_id}", parameters=None
        )
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(f"Observation with id {observation_id} not found")
        return ObservationResponse(
            **result.body_dict_or_error(f"Error fetching Observation with id {observation_id}.")
        )

    async def get_all_by_name(
        self, observation_name: str, dataset_id: int
    ) -> List[ObservationResponse]:
        results = await self.api.get(
            path=(
                f"{Constants.OBSERVATIONS_PATH}"
                f"?dataset_id={dataset_id}&file_name={observation_name}"
            ),
            parameters=None,
        )
        return ListObservationResponse(
            **results.body_dict_or_error("Failed to retrieve Observations.")
        ).items

    async def delete(self, observation_id: int) -> None:
        await self.api.delete(path=f"{Constants.OBSERVATIONS_PATH}/{observation_id}")
