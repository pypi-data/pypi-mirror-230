from typing import BinaryIO, List, Union

from aidkit_client._endpoints.constants import Constants
from aidkit_client._endpoints.models import (
    FrameworkType,
    ImageModelContextSpecs,
    ListMLModelResponse,
    ListMLModelVersionResponse,
    MLModelCreationRequestForSchema,
    MLModelResponse,
    MLModelVersionResponse,
    TextModelContextSpecs,
)
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.exceptions import ResourceWithIdNotFoundError


class MLModelsAPI:
    api: HTTPService

    def __init__(self, api: HTTPService):
        self.api = api

    async def get_all(self) -> List[MLModelResponse]:
        result = await self.api.get(path=Constants.ML_MODELS_PATH, parameters=None)
        return ListMLModelResponse(
            **result.body_dict_or_error("Failed to retrieve MLModels.")
        ).items

    async def get(self, model_id: int) -> MLModelResponse:
        result = await self.api.get(path=f"{Constants.ML_MODELS_PATH}/{model_id}", parameters=None)
        if result.is_not_found:
            raise ResourceWithIdNotFoundError(f"MLModel with id {model_id} not found")
        return MLModelResponse(
            **result.body_dict_or_error(f"Error fetching MLModel with id {model_id}. ")
        )

    async def get_all_model_versions(self, model_id: int) -> List[MLModelVersionResponse]:
        result = await self.api.get(
            path=f"{Constants.ML_MODELS_PATH}/{model_id}/versions", parameters=None
        )

        return ListMLModelVersionResponse(
            **result.body_dict_or_error("Failed to retrieve MLModel versions.")
        ).items

    async def update(self, model_id: int, new_name: str) -> MLModelResponse:
        result = await self.api.patch(
            path=f"{Constants.ML_MODELS_PATH}/{model_id}",
            parameters=None,
            body={"name": new_name},
        )
        if result.is_bad:
            raise ResourceWithIdNotFoundError(f"Could not update MLModel name with id {model_id}")
        return MLModelResponse(
            **result.body_dict_or_error(f"Error patching MLModel with id {model_id}.")
        )

    async def upload_model_version(
        self, model_id: int, model_version_name: str, model_file_content: BinaryIO, file_name: str
    ) -> MLModelVersionResponse:

        result = await self.api.post_multipart_data(
            path=f"{Constants.ML_MODELS_PATH}/{model_id}/versions",
            data={"name": model_version_name},
            files={"model": (f"{file_name}", model_file_content)},
        )
        if result.is_bad:
            raise ResourceWithIdNotFoundError(
                f"Could not upload version '{model_version_name}' of MLModel '{model_id}'."
            )
        return MLModelVersionResponse(
            **result.body_dict_or_error(
                f"Error uploading version '{model_version_name}' of MLModel '{model_id}'."
            )
        )

    async def create_model(
        self,
        model_name: str,
        model_version_name: str,
        framework: FrameworkType,
        context: Union[ImageModelContextSpecs, TextModelContextSpecs],
        model_file_content: BinaryIO,
    ) -> MLModelResponse:

        # Schema cannot be changed because it is derived from the request in
        # the MLModelPresenter, so that we pass empty bytes to the non-used
        # model argument.
        model_creation_request = MLModelCreationRequestForSchema(
            model=bytes(),
            name=model_name,
            version_name=model_version_name,
            context=context,
            framework=framework,
        )
        # model_creation_request is used for encoding the context as json but cannot be passed
        # on directly to the server because the model file binary cannot be encoded in json
        result = await self.api.post_multipart_data(
            path=f"{Constants.ML_MODELS_PATH}",
            data={
                "name": model_creation_request.name,
                "version_name": model_creation_request.version_name,
                "context": model_creation_request.context.json(),
                "framework": model_creation_request.framework.value,
            },
            files={"model": model_file_content},
        )

        return MLModelResponse(
            **result.body_dict_or_error(
                f"Error creating MLModel '{model_name}'"
                f" or uploading model version '{model_version_name}'."
            )
        )

    async def delete(self, model_id: int) -> bool:
        response = await self.api.delete(path=f"{Constants.ML_MODELS_PATH}/{model_id}")
        return response.is_success

    async def delete_model_version(self, model_id: int, model_version_id: int) -> bool:
        response = await self.api.delete(
            path=f"{Constants.ML_MODELS_PATH}/{model_id}/versions/{model_version_id}"
        )

        if response.is_not_found:
            raise ResourceWithIdNotFoundError(
                f"Could not delete MLModel version '{model_version_id}'"
            )

        return response.is_success
