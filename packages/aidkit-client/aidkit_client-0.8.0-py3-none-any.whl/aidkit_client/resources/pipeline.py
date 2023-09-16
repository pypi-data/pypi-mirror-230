"""
A pipeline on aidkit consists of analyses and evaluations. Pipelines must be
configured using the web GUI. After a pipeline has been configured, it can be
run on a data subset and a machine learning model version of choice using the
python client.

Running a pipeline on a machine learning model and a data subset creates
a pipeline run. Finishing a pipeline run creates a report, which
contains information about the evaluations and can be used to download
adversarial examples.
"""

import asyncio
from enum import Enum
from time import time
from typing import List, Optional, Tuple, Union

import pandas as pd
from tqdm import tqdm

from aidkit_client._endpoints.models import (
    IdentifierInput,
    PipelineRunResponse,
    PipelineRunState,
    RequiredContextDescription,
    TargetClassInput,
    UserProvidedContext,
)
from aidkit_client._endpoints.pipeline_runs import PipelineRunsAPI
from aidkit_client._endpoints.pipelines import PipelineResponse, PipelinesAPI
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.configuration import get_api_client
from aidkit_client.exceptions import (
    AidkitClientError,
    RunTimeoutError,
    TargetClassNotPassedError,
)
from aidkit_client.resources.dataset import Subset
from aidkit_client.resources.ml_model import MLModelVersion


class PipelineRun:
    """
    A run of a pipeline.

    An instance of this class references a pipeline run on the server
    which has been created by running a pipeline.
    """

    def __init__(
        self, api_service: HTTPService, pipeline_run_response: PipelineRunResponse
    ) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communcation with the
            server.
        :param pipeline_run_response: Server response describing the pipeline
            run to be created.
        """
        self._data = pipeline_run_response
        self._api_service = api_service

    @classmethod
    async def get_by_id(cls, pipeline_run_id: int) -> "PipelineRun":
        """
        Get a pipeline run by its reference id on the aidkit server.

        :param pipeline_run_id: Reference ID of the pipeline run to fetch.
        :return: Instance of the pipeline with the given id.
        """
        api_service = get_api_client()
        response = await PipelineRunsAPI(api_service).get(pipeline_run_id)
        return PipelineRun(api_service, response)

    async def get_progress(self) -> pd.DataFrame:
        """
        Get the progress report of a pipeline run. The report shows the state
        of each analysis method. For running methods, the elapsed time is
        shown. For finished methods, the total runtime is shown.

        :return: The progress report
        """
        response = await PipelineRunsAPI(self._api_service).get(self._data.id)

        column_name_mapper = {
            "method": "Analysis Method",
            "parameters": "Method Parameters",
            "elapsed_time_absolute": "Elapsed Time Absolute",
            "elapsed_time_relative": "Elapsed Time Relative (%)",
            "estimated_time_remaining": "Estimated Time Remaining",
        }
        progress_report = pd.DataFrame.from_dict(response.progress_report)
        progress_report.rename(columns=column_name_mapper, inplace=True)
        return progress_report

    async def get_state(self) -> Tuple[PipelineRunState, str]:
        """
        Get the state of the pipeline run.

        A pipeline can be either:

        * Stopped, if it got stopped by manual user intervention
        * Failed, if an analysis or evaluation failed
        * Running, if it is still running and not finished yet
        * Success, if it finished successfully
        * Pending, if it waits for execution

        :return: State of the pipeline run, error message describing all
                errors that occurred during the run
        """
        # if one node is stopped, the whole run is stopped
        # else, if any node is running, the whole pipeline is running
        # otherwise, it's either pending or finished
        response = await PipelineRunsAPI(self._api_service).get(self._data.id)
        if response.error_message is None:
            state_message = "No errors to report."
        else:
            state_message = response.error_message

        return response.state, state_message

    async def wait_to_finish(
        self,
        pipeline_finish_timeout: Optional[int] = None,
        progress_bar: bool = False,
    ) -> None:
        """
        Wait for the pipeline run to finish and throw an error if the pipeline
        does not finish in time.

        :param pipeline_finish_timeout: Number of seconds to wait for the
            pipeline run to finish. If the pipeline run is not finished after
            ``pipeline_finish_timeout`` number of seconds, a ``RunTimeoutError``
            is raised.
        :param progress_bar: Whether to display a progress bar when waiting for
            the pipeline to finish.
        :raises RunTimeoutError: If ``pipeline_finish_timeout`` seconds have
            passed, but the pipeline run is not finished yet.
        :return: Return if pipeline finishes
        """

        async def get_progress_percentage() -> float:
            """
            :return: Pipeline progress percentage.
            """
            response = await PipelineRunsAPI(self._api_service).get(self._data.id)

            return response.progress

        starting_time = time()
        current_time = starting_time

        last_progress = 0
        # the below is not missing an f-prefix, but is a format string for tqdm
        status_bar_format = (
            "{desc}: {percentage:3.0f}%|{bar}| "  # noqa: FS003
            "{n_fmt}/{total_fmt} [{elapsed}]"  # noqa: FS003
        )
        with tqdm(
            total=100,
            disable=not progress_bar,
            desc="Pipeline Run progress",
            miniters=1,
            mininterval=0,
            bar_format=status_bar_format,
        ) as pbar:
            while (
                pipeline_finish_timeout is None
                or current_time - starting_time < pipeline_finish_timeout
            ):
                progress_percentage = int(await get_progress_percentage())
                # keep the elapsed time at x.5 for consistent tqdm "elapsed time" updates
                await asyncio.sleep((starting_time - time()) % 1 + 0.5)
                pbar.update(progress_percentage - last_progress)
                # without refreshing, tqdm will not update the elapsed time unless there is progress
                pbar.refresh()
                last_progress = progress_percentage
                if progress_percentage == 100:
                    return
                current_time = time()
        raise RunTimeoutError(
            f"Pipeline has not finished after the timeout of {pipeline_finish_timeout} seconds."
        )

    @property
    def id(self) -> int:
        """
        Get the ID the instance is referenced by on the server.

        :return: ID of the instance
        """
        return self._data.id


class _ContextNames(Enum):
    ML_MODEL_VERSION = "ml_model_version_identifier"
    SUBSET = "subset_identifier"


_TARGET_CLASS_NAME = "TargetClassInput"


class Pipeline:
    """
    A pipeline.

    An instance of this class references a pipeline on the server which
    has been created in the web GUI.
    """

    def __init__(self, api_service: HTTPService, pipeline_response: PipelineResponse) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communication with the
            server.
        :param pipeline_response: Server response describing the pipeline
            to be created.
        """
        self._data = pipeline_response
        self._api_service = api_service

    @classmethod
    async def get_all(cls) -> List["Pipeline"]:
        """
        Get all Pipelines.

        :return: List of Pipelines
        """
        api_service = get_api_client()
        return [
            Pipeline(api_service, response)
            for response in await PipelinesAPI(api_service).get_all()
        ]

    @classmethod
    async def get_by_id(cls, pipeline_id: int) -> "Pipeline":
        """
        Get a pipeline by its reference ID on the aidkit server.

        :param pipeline_id: Reference ID of the pipeline to fetch
        :return: Instance of the pipeline with the given ID.
        """
        api_service = get_api_client()
        pipeline_response = await PipelinesAPI(api_service).get_by_id(pipeline_id)
        return Pipeline(api_service, pipeline_response)

    @property
    def id(self) -> int:
        """
        Get the ID the instance is referenced by on the server.

        :return: ID of the instance
        """
        return self._data.id

    @property
    def name(self) -> str:
        """
        Get the name the instance.

        :return: Name of the instance
        """
        return self._data.name

    async def run(
        self,
        model_version: Union[int, MLModelVersion],
        subset: Union[int, Subset],
        target_class: Optional[int] = None,
    ) -> PipelineRun:
        """
        Run the pipeline with a specific model version and a specific subset.

        :param model_version: Model version to run the pipeline with.
            If an integer is passed, it is interpreted as the model version id.
        :param subset: Subset to run the pipeline with.
            If an integer is passed, it is interpreted as the subset id.
        :param target_class: Index of the target class to run the pipeline with.
            Some analyses need to be given a target class to run them. If such
            an analysis is contained in the pipeline, the index of the target
            class to run the analysis with must be passed. If the pipeline
            requires a target class index but `None` is passed, this method
            raises a `TargetClassNotPassedError`.
        :return: The pipeline run created by running the pipeline.
        """
        if isinstance(model_version, MLModelVersion):
            model_version_id = model_version.id
        else:
            model_version_id = model_version
        if isinstance(subset, Subset):
            subset_id = subset.id
        else:
            subset_id = subset
        required_context = self._data.context

        def required_context_to_context_mapper(
            required_context: RequiredContextDescription,
        ) -> UserProvidedContext:
            required_context_name = required_context.context_name
            context_value: Union[IdentifierInput, TargetClassInput]
            if required_context_name == _ContextNames.ML_MODEL_VERSION.value:
                context_value = IdentifierInput(value=model_version_id)
            elif required_context_name == _ContextNames.SUBSET.value:
                context_value = IdentifierInput(value=subset_id)
            elif required_context.context_type["title"] == _TARGET_CLASS_NAME:
                if target_class is None:
                    raise TargetClassNotPassedError("Pipeline requires a target class to be set")
                context_value = TargetClassInput(value=target_class)
            else:
                raise AidkitClientError(
                    f"Unknown context type '{required_context.context_type['title']}' required "
                    f"under context name {required_context_name}"
                )
            return UserProvidedContext(
                pipeline_node_id=required_context.pipeline_node_id,
                context_name=required_context.context_name,
                value=context_value,
            )

        context = map(required_context_to_context_mapper, required_context)
        pipeline_response = await PipelineRunsAPI(self._api_service).run_pipeline(
            self.id, context=list(context)
        )
        return PipelineRun(self._api_service, pipeline_response)

    @classmethod
    async def delete(cls, pipeline_id: int) -> None:
        """
        Delete a pipeline.

        :param pipeline_id: int
        :return: None
        """
        await PipelinesAPI(get_api_client()).delete(pipeline_id)
