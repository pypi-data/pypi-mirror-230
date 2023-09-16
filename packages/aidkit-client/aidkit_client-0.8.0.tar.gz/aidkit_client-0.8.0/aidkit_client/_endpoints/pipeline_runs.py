from typing import List

from aidkit_client._endpoints.constants import Constants
from aidkit_client._endpoints.models import (
    CreatePipelineRunRequest,
    PipelineRunListResponse,
    PipelineRunResponse,
    UserProvidedContext,
)
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.exceptions import ResourceWithIdNotFoundError


class PipelineRunsAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def get_all(self) -> List[PipelineRunResponse]:
        result = await self.api.get(path=Constants.PIPELINE_RUNS_PATH, parameters=None)
        return PipelineRunListResponse(
            **result.body_dict_or_error("Failed to retrieve PipelineRuns.")
        ).items

    async def run_pipeline(
        self, pipeline_id: int, context: List[UserProvidedContext]
    ) -> PipelineRunResponse:
        body = CreatePipelineRunRequest(pipeline_id=pipeline_id, context=context).dict()
        result = await self.api.post_json(
            path=Constants.PIPELINE_RUNS_PATH,
            body=body,
            parameters=None,
        )
        return PipelineRunResponse(
            **result.body_dict_or_error(f"Failed to create PipelineRun with ID {pipeline_id}.")
        )

    async def get(self, pipeline_run_id: int) -> PipelineRunResponse:
        result = await self.api.get(
            path=f"{Constants.PIPELINE_RUNS_PATH}/{pipeline_run_id}", parameters=None
        )
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(f"PipelineRun with ID: {pipeline_run_id} not found")
        return PipelineRunResponse(
            **result.body_dict_or_error(f"Error fetching PipelineRun with ID {pipeline_run_id}.")
        )

    async def delete(self, pipeline_run_id: int) -> bool:
        response = await self.api.delete(path=f"{Constants.PIPELINE_RUNS_PATH}/{pipeline_run_id}")
        return response.is_success
