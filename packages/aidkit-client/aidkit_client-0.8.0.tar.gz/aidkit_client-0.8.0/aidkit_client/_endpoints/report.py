from aidkit_client._endpoints.constants import Constants
from aidkit_client._endpoints.models import (
    ReportAdversarialResponse,
    ReportCoreMethodOutputDetailResponse,
    ReportCorruptionResponse,
    ReportRequest,
)
from aidkit_client.aidkit_api import HTTPService


class ReportAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def get_corruption_report(self, request: ReportRequest) -> ReportCorruptionResponse:
        result = await self.api.post_json(
            path=f"{Constants.REPORT_PATH}/corruptions",
            parameters=None,
            body=request.dict(),
        )
        return ReportCorruptionResponse(
            **result.body_dict_or_error(
                f"Error fetching Corruption Report for model '{request.model}'."
            )
        )

    async def get_adversarial_report(self, request: ReportRequest) -> ReportAdversarialResponse:
        result = await self.api.post_json(
            path=f"{Constants.REPORT_PATH}/adversarial_examples",
            parameters=None,
            body=request.dict(),
        )
        return ReportAdversarialResponse(
            **result.body_dict_or_error(
                f"Error fetching Adversarial Report for model '{request.model}'."
            )
        )

    async def get_perturbed_observation_details(
        self, perturbed_observation_id: int
    ) -> ReportCoreMethodOutputDetailResponse:
        result = await self.api.get(
            path=f"{Constants.REPORT_PATH}/artifact_details/{perturbed_observation_id}",
            parameters=None,
        )
        return ReportCoreMethodOutputDetailResponse(
            **result.body_dict_or_error(
                f"Error fetching inference results for remote file '{perturbed_observation_id}'."
            )
        )
