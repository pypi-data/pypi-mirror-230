"""
A dataset is a collection of observations of the same type.

A subset is a set of observations. Observations of a dataset can be part
of multiple overlapping subsets.
"""
import asyncio
import io
from enum import Enum
from hashlib import md5
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterable, List, Optional, Sequence, Tuple, Union
from warnings import warn

import numpy as np
from PIL import Image
from tenacity import retry, stop_after_attempt
from tqdm import tqdm

from aidkit_client._endpoints.datasets import DatasetAPI
from aidkit_client._endpoints.models import DatasetResponse, ObservationResponse
from aidkit_client._endpoints.models import ObservationType as _InternalObservationType
from aidkit_client._endpoints.models import SegmentationMapResponse, SubsetResponse
from aidkit_client._endpoints.observations import ObservationAPI
from aidkit_client._endpoints.segmentation_maps import SegmentationMapAPI
from aidkit_client._endpoints.subsets import SubsetAPI
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.configuration import get_api_client
from aidkit_client.exceptions import AidkitClientError
from aidkit_client.resources.data_point import DataPointType, RemoteFile


class ObservationType(Enum):
    """
    Identification of the type of an observation.
    """

    TEXT = "TEXT"
    COLOR_IMAGE = "COLOR_IMAGE"
    GREY_SCALE_IMAGE = "GREY_SCALE_IMAGE"


def _to_internal_observation_type(obs_type: ObservationType) -> _InternalObservationType:
    """
    Convert an instance of the `resources.dataset.ObservationType` enum - which
    is part of the stable aidkit client API - to an instance of
    `_endpoints.models.ObservationType` - which is part of the aidkit web API.

    :param obs_type: Instance to be converted.
    :return: Corresponding instance which can be used in the web API.
    """
    if obs_type is ObservationType.TEXT:
        return _InternalObservationType.TEXT
    if obs_type is ObservationType.COLOR_IMAGE:
        return _InternalObservationType.COLOR_IMAGE
    if obs_type is ObservationType.GREY_SCALE_IMAGE:
        return _InternalObservationType.GREY_SCALE_IMAGE
    return None


def _bytes_to_hash(bytes_to_hash: bytes) -> str:
    # we are fine with using an unsafe hash function
    md5_hash = md5()  # noqa
    md5_hash.update(bytes_to_hash)
    return md5_hash.hexdigest()


def _observation_to_file_object_and_name(observation: Any) -> Tuple[BinaryIO, str]:
    if isinstance(observation, Path):
        #  using a context manager doesn't work here
        return (open(observation, "rb"), observation.name)  # pylint: disable=consider-using-with
    if isinstance(observation, str):
        str_in_bytes = observation.encode("UTF-8")
        return (io.BytesIO(str_in_bytes), _bytes_to_hash(str_in_bytes))
    if isinstance(observation, bytes):
        return (io.BytesIO(observation), _bytes_to_hash(observation))
    if isinstance(observation, Image.Image):
        bio = io.BytesIO()
        observation.save(bio, format="PNG")
        bio.seek(0)
        if hasattr(observation, "filename"):
            name = Path(observation.filename).name
        else:
            name = _bytes_to_hash(bio.getvalue())
        return (bio, name)

    raise ValueError(
        f"Loading an observation of type {type(observation)} is currently not supported."
    )


class SegmentationMap:
    """
    A segmentation map.
    """

    def __init__(
        self, api_service: HTTPService, segmentation_map_response: SegmentationMapResponse
    ) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communicating with the
            server.
        :param segmentation_map_response: Server response describing the segmentation map
            to be created.
        """
        self._data = segmentation_map_response
        self._api_service = api_service

    @classmethod
    async def create(
        cls, observation: Union["Observation", int], class_names: List[str], data: List[List[int]]
    ) -> "SegmentationMap":
        """
        Create a segmentation map.

        :param observation: Observation linked to this segmentation map. If an integer is passed,
            it is interpreted as an observation ID.
        :param class_names: List of class names for the segmentation map.
        :param data: Segmentation map passed as a 2D list of strings.
        :raises ValueError: If the segmentation map provided contains negative values or if the
            class names list has less elements than the largest index in the segmentation map
        :return: Segmentation map created.
        """
        data_array = np.array(data)
        if not np.all(data_array >= 0):
            raise ValueError("The segmentation map data provided contains negative values.")

        if np.max(data_array) >= len(class_names):
            raise ValueError(
                "The given segmentation map contains class indices larger than the given number of "
                "class names"
            )
        if data_array.ndim != 2:
            raise ValueError("The given segmentation map data is not a two dimensional array")

        if isinstance(observation, Observation):
            observation = observation.id

        api_service = get_api_client()
        segmentation_map_response = await SegmentationMapAPI(api_service).create(
            observation_id=observation, segmentation_map_data=data, class_names=class_names
        )

        return SegmentationMap(
            api_service=api_service, segmentation_map_response=segmentation_map_response
        )

    def as_remote_file(self) -> RemoteFile:
        """
        Get the corresponding remote file, which can be used to download the
        segmentation map.

        :return: RemoteFile corresponding to the segmentation_map.
        :raises AidkitClientError: If the segmentation map URL is not set.
        """
        if self._data.file_url is None:
            raise AidkitClientError(f"Segmentation with id {self.id} has no url.")
        return RemoteFile(url=self._data.file_url, type=DataPointType.SEGMENTATION_MAP_DATA)

    @property
    def id(self) -> int:
        """
        Get the ID of the segmentation map.

        :return: ID of the segmentation map.
        """
        return self._data.id

    @property
    def observation_id(self) -> int:
        """
        Get the ID of the observation for this segmentation map.

        :return: ID of the observation for this segmentation map.
        """
        return self._data.observation_id

    @property
    def class_names(self) -> List[str]:
        """
        Class names for this segmetation map.

        :return: Class names for this segmentation map.
        """
        return self._data.class_names


class Observation:
    """
    An observation.

    An instance of this class references an observation.
    """

    def __init__(self, api_service: HTTPService, observation_response: ObservationResponse) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communicating with the
            server.
        :param observation_response: Server response describing the observation
            to be created.
        """
        self._data = observation_response
        self._api_service = api_service

    @classmethod
    async def create(
        cls,
        dataset: Union["Dataset", int],
        file: Any,
        observation_type: ObservationType,
        subsets: Sequence[Union["Subset", int]],
        name: Optional[str] = None,
        odd_tags: Optional[List[str]] = None,
        segmentation_map: Optional[Tuple[List[str], List[List[int]]]] = None,
    ) -> "Observation":
        """
        Create and upload a single observation.

        :param dataset: Dataset to add the observation to. An integer is
            interpreted as the dataset ID.
        :param file: Observation to upload. How this parameter is interpreted
            depends on its type:

            * If the parameter is a string, it is interpreted as a
                text-observation to be uploaded.
            * If the parameter is a ``PIL.Image``, it is interpreted as a PNG
                image to be uploaded.
            * If the parameter is a ``pathlib.Path``, it is interpreted as the
                path of the observation file to be uploaded.
            * If the parameter is a ``bytes``-object, it is uploaded unchanged.

        :param observation_type: Type of the observation to add.
        :param subsets: List of subsets to include this observation in.
            Integers are interpreted as subset IDs.
        :param name: Name of the observation to create. If set to None, a name
            is autogenerated by the following rule:

            * If the ``file`` parameter is an instance of ``pathlib.Path``, the
                file name is used.
            * If the ``file`` parameter is an instance of ``PIL.Image`` and has
                an attribute ``filename``, ``file.filename`` is used.
                This is the case if the ``file`` argument has been created
                using ``PIL.Image.open``.
            * Otherwise, the MD5 hash of the ``file`` attribute converted to
                bytes, is computed. The hex representation of this hash is used
                as observation name.

        :param odd_tags: List of tags from the Operational Design Domain (ODD)
            that apply to this observation.
        :param segmentation_map: Optional tuple `(class_names, segmentation_map)` where
            `class_names` is a list of strings and `segmentation_map` is a 2D array of class
            indices.
        :raises AidkitClientError: If the observation is a text and a segmentation map is given.
        :return: Created observation.
        """
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        subset_ids = [subset if isinstance(subset, int) else subset.id for subset in subsets]

        api_service = get_api_client()
        observation_file_object, name_from_file = _observation_to_file_object_and_name(file)
        if name is None:
            name = name_from_file

        observation_response = await ObservationAPI(api_service).create(
            dataset_id=dataset,
            observation_type=_to_internal_observation_type(observation_type),
            subset_ids=subset_ids,
            odd_tags=odd_tags,
            obs_name=name,
            obs_data=observation_file_object,
        )

        if segmentation_map:
            class_names, segmentation_map_data = segmentation_map

            if observation_type in [ObservationType.COLOR_IMAGE, ObservationType.GREY_SCALE_IMAGE]:
                observation_shape = Image.open(observation_file_object).size
                # For some reason, PIL reports (width, height) instead of (height, width)
                observation_shape = (observation_shape[1], observation_shape[0])
                segmentation_map_data_shape = np.shape(segmentation_map_data)
                if observation_shape != segmentation_map_data_shape:
                    warn(
                        f"The provided segmentation map has shape {segmentation_map_data_shape} "
                        f"which is not equal to the size of the provided image {observation_shape}."
                        " This might result in errors when running a pipeline"
                    )
            else:
                raise AidkitClientError(
                    "Segmentation maps can only be used with image observations."
                )

            _ = await SegmentationMap.create(
                observation=observation_response.id,
                class_names=class_names,
                data=segmentation_map_data,
            )

        return Observation(api_service=api_service, observation_response=observation_response)

    @classmethod
    async def get_by_id(cls, observation_id: int) -> "Observation":
        """
        Get an observation by its ID.

        :param observation_id: ID of the observation to fetch.
        :return: Instance of the observation with the given ID.
        """
        api_service = get_api_client()
        pipeline_response = await ObservationAPI(api_service).get_by_id(observation_id)
        return Observation(api_service, pipeline_response)

    @classmethod
    async def get_all_by_name(
        cls, name: str, dataset: Union[int, "Dataset"]
    ) -> List["Observation"]:
        """
        Get a list of observations by their name.

        :param name: Name of the observations queried.
        :param dataset: Dataset in which the observation is. Integer interpreted as dataset ID.
        :return: List of observations with the provided name.
        """
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        api_service = get_api_client()
        pipeline_responses = await ObservationAPI(api_service).get_all_by_name(name, dataset)
        return [
            Observation(api_service, pipeline_response) for pipeline_response in pipeline_responses
        ]

    @classmethod
    async def delete(cls, observation_id: int) -> None:
        """
        Delete an observation.

        :param observation_id: ID of the observation to delete.
        :return: None.
        """
        await ObservationAPI(get_api_client()).delete(observation_id)

    def as_remote_file(self) -> RemoteFile:
        """
        Get the corresponding remote file, which can be used to download the
        observation.

        :return: RemoteFile corresponding to the observation.
        :raises AidkitClientError: If the observation type is unknown or the
            observation URL is not set.
        """
        if self._data.type in ["COLOR_IMAGE", "GREY_SCALE_IMAGE"]:
            data_point_type = DataPointType.IMAGE
        elif self._data.type == "TEXT":
            data_point_type = DataPointType.TEXT
        else:
            raise AidkitClientError(f"Unknown observation type {self._data.type}.")
        if self._data.file_url is None:
            raise AidkitClientError(f"Observation with id {self.id} has no url.")
        return RemoteFile(url=self._data.file_url, type=data_point_type)

    @property
    def id(self) -> int:
        """
        Get the ID of the observation.

        :return: ID of the observation.
        """
        return self._data.id

    @property
    def name(self) -> str:
        """
        Get the name the observation.

        :return: Name of the observation.
        """
        return self._data.file_name

    @property
    async def segmentation_map(self) -> SegmentationMap:
        """
        Get the segmentation map for this observation if it exists.

        :return: Segmentation map associated with the observation.
        """
        segmentation_map_response = await SegmentationMapAPI(
            self._api_service
        ).get_by_observation_id(self.id)
        return SegmentationMap(
            api_service=self._api_service, segmentation_map_response=segmentation_map_response
        )


class Subset:
    """
    A dataset subset.

    An instance of this class references a subset.
    """

    def __init__(self, api_service: HTTPService, subset_response: SubsetResponse) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communicating with the
            server.
        :param subset_response: response describing the subset
            to be created.
        """
        self._data = subset_response
        self._api_service = api_service

    @classmethod
    async def create(
        cls,
        name: str,
        dataset: Union["Dataset", int],
        observations: Sequence[Union[Observation, int]],
    ) -> "Subset":
        """
        Create a subset of a dataset.

        :param name: Name of the subset.
        :param dataset: Dataset to upload observations to. An integer is
            interpreted as the dataset ID.
        :param observations: Observations to be in the subset. Integers are
            interpreted as observation IDs.
        :return: Created subset.
        """
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        api_service = get_api_client()
        observation_ids = [obs if isinstance(obs, int) else obs.id for obs in observations]
        subset_response = await SubsetAPI(api_service).create(
            subset_name=name, dataset_id=dataset, observation_ids=observation_ids
        )
        return Subset(api_service=api_service, subset_response=subset_response)

    async def update(self, observations: Sequence[Union[Observation, int]]) -> "Subset":
        """
        Update the observations within a subset.

        :param observations: Observations to add to the dataset. Integers are
            interpreted as observation IDs.
        :return: Instance of the updated subset.
        """
        api_service = get_api_client()
        observation_ids = [obs if isinstance(obs, int) else obs.id for obs in observations]
        subset_response = await SubsetAPI(api_service).update(
            subset_id=self.id, observation_ids=observation_ids
        )
        return Subset(api_service=api_service, subset_response=subset_response)

    @classmethod
    async def get_by_id(cls, subset_id: int) -> "Subset":
        """
        Get a subset by its ID.

        :param subset_id: ID of the subset to create an instance of.
        :return: Instance of the subset with the given ID.
        """
        api_service = get_api_client()
        response = await SubsetAPI(api_service).get(subset_id)
        return Subset(api_service, response)

    @property
    def id(self) -> int:
        """
        Get the ID of the subset.

        :return: ID of the subset.
        """
        return self._data.id

    @property
    def name(self) -> str:
        """
        Get the name the subset.

        :return: Name of the subset.
        """
        return self._data.name

    @property
    def observation_ids(self) -> List[int]:
        """
        Get the IDs of the observations contained in the subset.

        :return: List of observation IDs in the subset.
        """
        return self._data.observation_ids

    @classmethod
    async def delete(cls, subset_id: int) -> None:
        """
        Delete a subset.

        :param subset_id: ID of the subset to delete.
        :return: None.
        """
        await SubsetAPI(get_api_client()).delete(subset_id)


class Dataset:
    """
    A dataset.

    An instance of this class references a dataset.
    """

    def __init__(self, api_service: HTTPService, dataset_response: DatasetResponse) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communicating with the
            server.
        :param dataset_response: Server response describing the dataset
            to be created.
        """
        self._data = dataset_response
        self._api_service = api_service

    @classmethod
    async def create(
        cls,
        dataset_name: str,
        dataset_type: ObservationType,
        files: Optional[Union[Dict[str, Any], List[Any]]] = None,
        subset_names: Optional[Sequence[Union[Subset, str]]] = None,
        progress_bar: bool = True,
        max_simultaneous_uploads: int = 5,
    ) -> Tuple["Dataset", List[Subset]]:
        """
        Create a dataset.

        :param dataset_name: Name of the dataset.
        :param dataset_type: Type of the dataset.
        :param files: Files to upload.
            Can be either a dictionary of the form ``{observation_name: file}``
            or a list of files to upload.

            How a file is interpreted depends on its type:

            * If a file is a string, it is interpreted as a text-observation to
                be uploaded.
            * If a file is a ``PIL.Image``, it is interpreted as an PNG image
                to be uploaded.
            * If a file is a ``pathlib.Path``, it is interpreted as the path of
                the observation file to be uploaded.
            * If a file is a ``bytes``-object, it is uploaded unchanged.

            If a list of files is passed, the names of the created observations
            are autogenerated by the following rule:

            * If a file is an instance of ``pathlib.Path``, the file name is
                used.
            * If a file is an instance of ``PIL.Image`` and has an attribute
                ``filename``, ``file.filename`` is used. This is the case if
                the file has been created using ``PIL.Image.open``.
            * Otherwise, the MD5 hash of the file converted to bytes is
                computed. The hex representation of this hash is used as
                observation name.

        :param subset_names: List of subsets to add in the dataset. Strings are
            interpreted as subset names. If the ``files`` argument is not
            ``None``, all the created observations are added to all the created
            subsets.
        :param progress_bar: If set to True, a progress bar is displayed.
        :param max_simultaneous_uploads: Maximum number of simultaneous uploads.
        :return: Tuple containing the created dataset and the list of created
            subsets (may be empty).
        """
        if subset_names is None:
            subset_names = []
        if files is None:
            files = []
        api_service = get_api_client()
        dataset_response = await DatasetAPI(api_service).create(
            dataset_name=dataset_name,
            dataset_type=_to_internal_observation_type(dataset_type),
        )
        dataset = Dataset(api_service=api_service, dataset_response=dataset_response)
        created_subsets = []

        for subset in subset_names:
            subset_name = subset if isinstance(subset, str) else subset.name
            created_subset = await dataset.create_subset(subset_name, [])
            created_subsets.append(created_subset)

        await dataset.upload_data(
            files,
            [subset.id for subset in created_subsets],
            progress_bar=progress_bar,
            max_simultaneous_uploads=max_simultaneous_uploads,
        )
        if subset_names or files:
            # reload the dataset to reflect the changes
            dataset = await Dataset.get_by_id(dataset.id)

        return dataset, created_subsets

    @classmethod
    async def delete(cls, dataset_id: int) -> None:
        """
        Delete a dataset.

        :param dataset_id: ID of the dataset to delete.
        :return: None.
        """
        await DatasetAPI(get_api_client()).delete(dataset_id)

    async def create_subset(
        self, name: str, observations: Sequence[Union[Observation, int]]
    ) -> Subset:
        """
        Create a subset of the dataset.

        :param name: Name of the subset to create.
        :param observations: Observations to be included in the subset.
            Integers are interpreted as observation IDs.
        :return: Created subset.
        """
        return await Subset.create(name=name, dataset=self.id, observations=observations)

    async def upload_data(
        self,
        files: Union[Dict[str, Any], List[Any]],
        subsets: Sequence[Union[Subset, int]],
        odd_tags: Optional[Sequence[Optional[List[str]]]] = None,
        segmentation_maps: Optional[Sequence[Optional[Tuple[List[str], List[List[int]]]]]] = None,
        progress_bar: bool = True,
        max_simultaneous_uploads: int = 5,
        n_retry: int = 3,
    ) -> List[Observation]:
        """
        Upload data to the dataset.

        :param files: Files to upload.
            Can be either a dictionary of the form ``{observation_name: file}``
            or a list of files to upload.

            How a file is interpreted depends on its type:

            * If a file is a string, it is interpreted as a text-observation to
                be uploaded.
            * If a file is a ``PIL.Image``, it is interpreted as a PNG image to
                be uploaded.
            * If a file is a ``pathlib.Path``, it is interpreted as the path of
                the observation file to be uploaded.
            * If a file is a ``bytes``-object, it is uploaded unchanged.

            If a list of files is passed, the names of the created observations
            are autogenerated by the following rule:

            * If a file is an instance of ``pathlib.Path``, the file name is
                used.
            * If a file is an instance of ``PIL.Image`` and has an attribute
                ``filename``, ``file.filename`` is used. This is the case if
                the file has been created using ``PIL.Image.open``.
            * Otherwise, the MD5 hash of the file converted to bytes is
                computed. The hex representation of this hash is used as
                observation name.

        :param subsets: List of subsets to include the observations in.
            Integers are interpreted as subset IDs.
        :param odd_tags: List of tags from the Operational Design Domain (ODD)
            for every observation that will be uploaded.
        :param segmentation_maps: Segmentation maps to be uploaded with the observations. Given as
            a list of optional tuples `(class_name, segmentation_map)` where class_names is a list
            of strings and segmentation_map is a 2D list of integers. If an item of the list is
            `None`, then no segmentation map is uploaded for the corresponding observation.
        :param progress_bar: If set to True, a progress bar is displayed.
        :param max_simultaneous_uploads: Maximum number of simultaneous uploads.
        :param n_retry: Number of times to retry an observation upload before
            reraising.
        :raises ValueError: If the number of ODD tags specified does not match
            the number of observations.
        :return: Created observations.
        """
        observations = []
        if isinstance(files, dict):
            name_and_files_list: List[Tuple[Optional[str], Any]] = list(files.items())
        else:
            name_and_files_list = [(None, file) for file in files]

        if not odd_tags:
            converted_odd_tags: Iterable[Optional[List[str]]] = [None for _ in name_and_files_list]
        else:
            if len(odd_tags) != len(files):
                raise ValueError(
                    (
                        "The number of provided odd_tags does not match the "
                        f"number of observations: ({len(odd_tags)} != {len(files)})"
                    )
                )
            converted_odd_tags = odd_tags

        if not segmentation_maps:
            segmentation_maps = [None for _ in name_and_files_list]
        else:
            if len(segmentation_maps) != len(files):
                raise ValueError(
                    (
                        "The number of provided segmentation maps does not match "
                        f"the number of observations: ({len(segmentation_maps)} != {len(files)})"
                    )
                )

        semaphore = asyncio.Semaphore(max_simultaneous_uploads)
        with tqdm(
            total=len(name_and_files_list), desc="Uploading files...", disable=not progress_bar
        ) as tqdm_progress_bar:

            @retry(
                stop=stop_after_attempt(n_retry),
                reraise=True,
            )
            async def upload_file(
                name: Optional[str],
                file: Any,
                odd_tags: Optional[List[str]],
                segmentation_map: Optional[Tuple[List[str], List[List[int]]]],
            ) -> Observation:
                async with semaphore:
                    obs = await Observation.create(
                        dataset=self.id,
                        file=file,
                        observation_type=ObservationType(self._data.type),
                        subsets=subsets,
                        name=name,
                        odd_tags=odd_tags,
                        segmentation_map=segmentation_map,
                    )
                    tqdm_progress_bar.update(1)
                    return obs

            observations = await asyncio.gather(
                *(
                    upload_file(name, file, odd_tags, segmentation_map)
                    for ((name, file), odd_tags, segmentation_map) in zip(
                        name_and_files_list, converted_odd_tags, segmentation_maps
                    )
                )
            )

        return observations

    @classmethod
    async def get_all(cls) -> List["Dataset"]:
        """
        Get all the datasets created in aidkit.

        :return: List of datasets.
        """
        api_service = get_api_client()
        return [
            Dataset(api_service, response) for response in await DatasetAPI(api_service).get_all()
        ]

    async def get_all_subsets(self) -> List["Subset"]:
        """
        Get all the subsets of the dataset.

        :return: List of subsets.
        """
        api_service = get_api_client()
        return [
            Subset(api_service, response)
            for response in await SubsetAPI(api_service).get_all(self.id)
        ]

    @classmethod
    async def get_by_id(cls, dataset_id: int) -> "Dataset":
        """
        Get a dataset by its ID.

        :param dataset_id: ID of the dataset to create an instance of.
        :return: Instance of the dataset with the given ID.
        """
        api_service = get_api_client()
        pipeline_response = await DatasetAPI(api_service).get(dataset_id)
        return Dataset(api_service, pipeline_response)

    @property
    def id(self) -> int:
        """
        Get the ID of the dataset.

        :return: ID of the dataset.
        """
        return self._data.id

    @property
    def name(self) -> str:
        """
        Get the name the dataset.

        :return: Name of the dataset.
        """
        return self._data.name
