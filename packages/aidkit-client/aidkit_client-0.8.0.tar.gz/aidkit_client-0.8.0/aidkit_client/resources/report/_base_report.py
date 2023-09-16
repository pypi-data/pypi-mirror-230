"""
Shared functionality for the adversarial and corruption reports.
"""

import json
import random
from typing import Dict, List, Optional, Set, Union

import numpy as np
import PIL.Image
from ipywidgets import widgets
from pandas import DataFrame

from aidkit_client._endpoints.models import (
    ClassificationModelOutput,
    ImageObjectDetectionModelOutput,
    ImageSegmentationModelOutput,
    OutputType,
    ReportAdversarialResponse,
    ReportCoreMethodOutputDetailResponse,
    ReportCorruptionResponse,
)
from aidkit_client._endpoints.report import ReportAPI
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.configuration import get_api_client
from aidkit_client.plotting.base_objects import (
    display_object_detection_box_count_widget,
    display_observation,
    display_selection_class_detection_widget,
    display_semantic_segmentation_inference_widget,
    display_static_observation_difference,
    display_table,
    display_warning_message,
    generate_color_list,
    get_segmentation_prediction,
)
from aidkit_client.resources.data_point import DataPointType, RemoteFile
from aidkit_client.resources.dataset import Observation
from aidkit_client.resources.ml_model import MLModel, MLModelVersion


class PerturbedObservationDetails:
    """
    Inference results from the report detail view corresponding to the original
    observation and a perturbed observation.
    """

    def __init__(
        self,
        api_service: HTTPService,
        perturbed_observation_details: ReportCoreMethodOutputDetailResponse,
    ) -> None:
        """
        Create a new instance from the server detailed response.

        :param api_service: Service instance to use for communicating with the
            server.
        :param perturbed_observation_details: Server response describing the inference results
            corresponding to a given perturbed observation.
        """
        self._api_service = api_service
        self._data = perturbed_observation_details

    @classmethod
    async def get_by_perturbed_observation_id(
        cls, perturbed_observation_id: int
    ) -> "PerturbedObservationDetails":
        """
        Get detailed information on a perturbed observation.

        Information consists of:

        * Underlying observation*
        * Inference result of observation*
        * Inference result of perturbed observation*
        * Functionality to load content of perturbed observation*

        :param perturbed_observation_id: ID of the perturbed observation.
        :return: Instance of PerturbedObservationDetails.
        """
        api_service = get_api_client()
        return PerturbedObservationDetails(
            api_service=api_service,
            perturbed_observation_details=await ReportAPI(
                api_service
            ).get_perturbed_observation_details(perturbed_observation_id=perturbed_observation_id),
        )

    @property
    def observation_id(self) -> int:
        """
        Get the ID of the original observation from which this perturbed
        observation was generated.

        :return: ID of the underlying observation.
        """
        return self._data.observation_id

    @property
    async def observation(self) -> Observation:
        """
        Get the original observation from which this perturbed observation was
        generated.

        :return: Instance of the underlying observation.
        """
        return await Observation.get_by_id(self.observation_id)

    @property
    def observation_inference_result(
        self,
    ) -> Union[
        ClassificationModelOutput, ImageSegmentationModelOutput, ImageObjectDetectionModelOutput
    ]:
        """
        Get the underlying observation inference results.

        :return: Instance containing the observation inference results.
        """
        return self._data.observation_inference_result

    @property
    def perturbed_observation_id(self) -> int:
        """
        Get the ID of the perturbed observation.

        :return: ID of the perturbed observation.
        """
        return self._data.core_method_output_id

    def perturbed_observation_as_remote_file(self) -> RemoteFile:
        """
        Get a perturbed observation as a RemoteFile object.

        :raises ValueError: if method output type is unknown.
        :return: Remote file.
        """
        if self._data.core_method_output_type in ["COLOR_IMAGE", "GREY_SCALE_IMAGE"]:
            data_type = DataPointType.IMAGE
        elif "TEXT" == self._data.core_method_output_type:
            data_type = DataPointType.TEXT
        else:
            raise ValueError(
                f"Unknown type for method output: '{self._data.core_method_output_type}'."
            )
        return RemoteFile(url=self._data.core_method_output_storage_url, type=data_type)

    @property
    def perturbed_observation_inference_result(
        self,
    ) -> Union[
        ClassificationModelOutput, ImageSegmentationModelOutput, ImageObjectDetectionModelOutput
    ]:
        """
        Get the perturbed observation inference results, i.e.: the softmax
        output of the model.

        :return: Instance containing the perturbed observation inference results.
        """
        return self._data.core_method_output_inference_result

    @property
    def inference_class_names(self) -> List[str]:
        """
        Class names for the classes in the inference result.

        :return: List of  class names.
        """
        return self._data.core_method_output_inference_result.class_names


class _BaseReport:
    """
    Base class for the corruption- and the adversarial report.
    """

    _data: Union[ReportCorruptionResponse, ReportAdversarialResponse]

    @property
    def data(self) -> DataFrame:
        """
        Get the data of the report.

        :return: DataFrame containing sample data for the report. The returned DataFrame has one row
            per combination of

            * Configured Method: All those perturbation methods which were run on all compared model
                versions and evaluated with all considered norms are included.
            * Observation: Observation: All observations in the subset the report is requested for.
            * Model Version: All model versions the report is requested for.
            * Metric Name: All norms the report is requested for.

            The returned DataFrame has the following columns:

            * ``successful``: Boolean; Whether the generated perturbation changed the model's
                prediction.
            * ``distance_metric_value``: Float; Distance between the perturbation and the original
                observation.
            * ``method_name``: Categorical; Name of the method used to create the perturbation.
            * ``param_string`` Categorical; Parameters for the method used to create the
                perturbation.
            * ``observation_id``: Integer; ID of the original observation the perturbation was
                created for.
            * ``artifact_id``: Integer; ID of the generated perturbation.
            * ``distance_metric_name``: Categorical; Name of the metric used to measure
                ``distance_metric_value``.
                One of the names in ``metric_names``.
            * ```model_version_id``: Integer; ID of the model version the perturbed observation
                was created for.
            * ```perturbation_type``: Categorical; Type of the perturbation, i.e.: 'Corruption'.
        """
        return DataFrame(self._data.report.data.dict()).astype(
            {
                "distance_metric_name": "category",
                "method_name": "category",
                "param_string": "category",
                "success_metric_type": "category",
                "target_class": "category",
                "perturbation_type": "category",
            }
        )

    @property
    def model(self) -> MLModel:
        return MLModel(get_api_client(), self._data.model)

    @property
    def model_versions(self) -> List[MLModelVersion]:
        return [
            MLModelVersion(get_api_client(), model_version_data)
            for model_version_data in self._data.model_versions
        ]

    def _get_param_dict_for_id(self, perturbed_observation_id: int) -> Dict:
        """
        Return the param string for the method used to generate a perturbed
        observation.

        :param perturbed_observation_id: ID of the perturbed observation.
        :return: Dictionary corresponding to the parameters of the method used to generate the
            perturbed observation.
        """
        return json.loads(
            self.data[self.data["artifact_id"] == perturbed_observation_id]["param_string"].iloc[0]
        )

    def _get_pipeline_info_for_id(self, perturbed_observation_id: int) -> Dict:
        param_dict = self._get_param_dict_for_id(perturbed_observation_id)
        model_version_id: int = self.data[self.data["artifact_id"] == perturbed_observation_id][
            "model_version_id"
        ].iloc[0]
        (model_version,) = [
            model_version
            for model_version in self.model_versions
            if model_version.id == model_version_id
        ]
        return {
            "Model": [f"Name: {self.model.name}<br>Version: {model_version.name}"],
            "Perturbation Type": [
                self.data[self.data["artifact_id"] == perturbed_observation_id][
                    "perturbation_type"
                ].iloc[0]
            ],
            "Method Name": [
                self.data[self.data["artifact_id"] == perturbed_observation_id]["method_name"].iloc[
                    0
                ]
            ],
            "Parameters": [param_dict],
        }

    def _get_metrics_for_id(self, perturbed_observation_id: int) -> Dict:
        metric_df = self.data[self.data["artifact_id"] == perturbed_observation_id][
            ["distance_metric_name", "distance_metric_value"]
        ]
        metrics = {
            row["distance_metric_name"]: [f"{row['distance_metric_value']:.2f}"]
            for _, row in metric_df.iterrows()
        }
        return metrics

    @staticmethod
    def _assemble_widgets_in_view(
        observation_widget: widgets.CoreWidget,
        widget_list: List[widgets.CoreWidget],
        widget_header: List[str],
        warning_message: Optional[str] = None,
    ) -> widgets.VBox:
        """
        Assemble the different widgets into a single view.

        :param observation_widget: Widget displaying the observations (possibly with inference).
        :param widget_list: List of widgets to display beneath the observations.
        :param widget_header: Titles for the widgets in widget_list.
        :param warning_message: Message to display as a warning at the top of the detail view.
        :return: The assembled view as widget.
        """
        header_widget = widgets.HTML(value="<h1>Detail View</h1>")
        assembled_widget_list = [header_widget]

        if warning_message:
            assembled_widget_list.append(display_warning_message(warning_message))

        assembled_widget_list.append(observation_widget)

        for i, widget in enumerate(widget_list):
            acc = widgets.Accordion(children=[widget], selected_index=0)
            acc.set_title(0, widget_header[i])

            acc.layout.width = "605px"
            assembled_widget_list.append(acc)
        return widgets.VBox(assembled_widget_list)

    async def fetch_random_detail_views(
        self, number_of_inference_results: int
    ) -> List[PerturbedObservationDetails]:
        """
        Fetch a number of random detail views for the perturbed observations of
        the report. If the report has fewer perturbed observations than
        specified, all detail views are returned.

        :param number_of_inference_results: Number of detail views to return.
        :return: List of details views.
        """
        perturbed_observation_ids = list(self.data["artifact_id"].unique())
        out = [
            await PerturbedObservationDetails.get_by_perturbed_observation_id(
                perturbed_observation_id=perturbed_observation_id
            )
            for perturbed_observation_id in random.SystemRandom().sample(
                perturbed_observation_ids,
                k=min(len(perturbed_observation_ids), number_of_inference_results),
            )
        ]
        return out

    def _set_warning_message_if_target_class_not_in_original_inference(
        self, perturbed_observation_id: int, classes_in_inference: Set[int]
    ) -> Optional[str]:
        """
        Display a warning message if the class targeted by the corruption is
        not present in the original inference.

        :param perturbed_observation_id: ID of the perturbed observation displayed in the
            detail view.
        :param classes_in_inference: Set of IDs of classes present in the model inference on the
            original observation.
        :return: A warning message to display if the target class for the corruption is not present
            in the model inference on the original observation, None otherwise.
        """
        warning_message = None
        param_dict = self._get_param_dict_for_id(perturbed_observation_id)
        if "Target class ID" in param_dict:
            if param_dict["Target class ID"] not in classes_in_inference:
                warning_message = (
                    f"The class id '{param_dict['Target class ID']}' is configured "
                    "as the target for the local corruption, but it does not appear in "
                    "the model predictions on the original observation. Thus, the "
                    "original and the perturbed observation are identical."
                )

        return warning_message

    async def _get_classification_detail_view(self, perturbed_observation_id: int) -> widgets.VBox:
        """
        Produce the classification detail view for a given perturbed
        observation.

        :param perturbed_observation_id: ID specifying the perturbed
            observation.
        :raises ValueError: If the inference result type is not classification.
        :return: View as ipython widget.
        """
        perturbed_obs_details = await (
            PerturbedObservationDetails.get_by_perturbed_observation_id(
                perturbed_observation_id=perturbed_observation_id
            )
        )
        perturbed_observation: PIL.Image.Image = await (
            perturbed_obs_details.perturbed_observation_as_remote_file().fetch_remote_file()
        )

        observation_resource = await perturbed_obs_details.observation
        observation: PIL.Image.Image = (
            await observation_resource.as_remote_file().fetch_remote_file()
        )

        if not isinstance(
            perturbed_obs_details.observation_inference_result, ClassificationModelOutput
        ) or not isinstance(
            perturbed_obs_details.perturbed_observation_inference_result,
            ClassificationModelOutput,
        ):
            raise ValueError("Model task is wrongly configured.")

        original_observation_widget = display_observation(
            observation=observation,
            title="<center><b>Original Observation</b></center>",
            caption=[("ID", str(observation_resource.id)), ("File", observation_resource.name)],
        )
        perturbed_observation_widget = display_observation(
            observation=perturbed_observation,
            title="<center><b>Perturbed Observation</b></center>",
            caption=[("ID", str(perturbed_observation_id))],
        )

        if isinstance(observation, str):
            observation_box = widgets.VBox
        else:
            observation_box = widgets.HBox

        observation_box_widget = observation_box(
            [
                original_observation_widget,
                perturbed_observation_widget,
            ]
        )

        difference_widget = display_static_observation_difference(
            original=observation, perturbed=perturbed_observation
        )

        class_names = perturbed_obs_details.inference_class_names

        observation_inference_result = perturbed_obs_details.observation_inference_result.data
        perturbed_inference_result = (
            perturbed_obs_details.perturbed_observation_inference_result.data
        )

        top_inference_classes = (
            list(np.array(observation_inference_result).argsort())[-5:]
            + list(np.array(perturbed_inference_result).argsort())[-5:]
        )

        prediction_original = np.array(observation_inference_result).argmax()
        prediction_perturbed = np.array(perturbed_inference_result).argmax()

        inference_table: Dict[str, List[Union[str, float, int]]] = {
            str(class_names[i]): [
                f"{float(observation_inference_result[i]):.2f}",
                f"{float(perturbed_inference_result[i]):.2f}",
            ]
            for i in set(top_inference_classes)
        }
        inference_table_header = ["Original", "Perturbed"]
        prediction_highlight = {str(class_names[prediction_original]): {0: "#c0edc0"}}
        if prediction_original == prediction_perturbed:
            prediction_highlight[str(class_names[prediction_perturbed])][1] = "#c0edc0"
        else:
            prediction_highlight[str(class_names[prediction_perturbed])] = {1: "#c0edc0"}
        inference_table_widget = display_table(
            data=inference_table,
            header=inference_table_header,
            highlight_cells=prediction_highlight,
        )
        metrics_table_widget = display_table(
            data=self._get_metrics_for_id(perturbed_observation_id)
        )
        pipeline_info_table_widget = display_table(
            data=self._get_pipeline_info_for_id(perturbed_observation_id)
        )

        view_elements = [
            inference_table_widget,
            metrics_table_widget,
            pipeline_info_table_widget,
            difference_widget,
        ]
        view_element_headers = [
            "Model Inference",
            "Perturbation Size",
            "Perturbation Details",
            "Difference Between Original and Perturbed Observation",
        ]

        return self._assemble_widgets_in_view(
            observation_widget=observation_box_widget,
            widget_list=view_elements,
            widget_header=view_element_headers,
        )

    async def _get_semantic_segmentation_detail_view(
        self, perturbed_observation_id: int
    ) -> widgets.VBox:
        """
        Produce the semantic segmentation detail view for a given perturbed
        observation.

        :param perturbed_observation_id: ID specifying the perturbed
            observation.
        :raises ValueError: If the inference result type is not segmentation.
        :return: View as ipython widget.
        """
        adversarial_example_details = await (
            PerturbedObservationDetails.get_by_perturbed_observation_id(
                perturbed_observation_id=perturbed_observation_id
            )
        )
        perturbed_observation: PIL.Image.Image = await (
            adversarial_example_details.perturbed_observation_as_remote_file().fetch_remote_file()
        )

        observation_resource = await adversarial_example_details.observation
        observation: PIL.Image.Image = (
            await observation_resource.as_remote_file().fetch_remote_file()
        )

        if not isinstance(
            adversarial_example_details.observation_inference_result, ImageSegmentationModelOutput
        ) or not isinstance(
            adversarial_example_details.perturbed_observation_inference_result,
            ImageSegmentationModelOutput,
        ):
            raise ValueError("Model task is wrongly configured.")

        # Display the original and perturbed observation side by side
        original_observation_widget = display_observation(
            observation=observation,
            title="<center><b>Original Observation</b></center>",
            caption=[("ID", str(observation_resource.id)), ("File", observation_resource.name)],
        )
        perturbed_observation_widget = display_observation(
            observation=perturbed_observation,
            title="<center><b>Perturbed Observation</b></center>",
            caption=[("ID", str(perturbed_observation_id))],
        )

        observation_box_widget = widgets.HBox(
            [
                original_observation_widget,
                perturbed_observation_widget,
            ]
        )

        # Perform a fex computation to display in the detail view
        target_classes = adversarial_example_details.inference_class_names
        n_classes = len(target_classes)

        # Get the list of colors for the classes
        class_colors = generate_color_list(n_classes)

        # Transform the inference data into numpy arrays
        original_inference_array = np.array(
            adversarial_example_details.observation_inference_result.data
        )
        perturbed_inference_array = np.array(
            adversarial_example_details.perturbed_observation_inference_result.data
        )

        inference_image, classes_in_original = get_segmentation_prediction(
            inference_result=original_inference_array, class_colors=class_colors
        )
        perturbed_inference_image, classes_in_perturbed = get_segmentation_prediction(
            inference_result=perturbed_inference_array, class_colors=class_colors
        )
        classes_in_inference = classes_in_original.union(classes_in_perturbed)

        # Check if the target class of the corruption is present in the original inference
        # otherwise display a warning.
        warning_message = self._set_warning_message_if_target_class_not_in_original_inference(
            perturbed_observation_id, classes_in_original
        )

        # Compute the coverage metrics
        coverage_original = (
            np.bincount(original_inference_array.flatten(), minlength=n_classes)
            / original_inference_array.size
        )
        coverage_perturbed = (
            np.bincount(perturbed_inference_array.flatten(), minlength=n_classes)
            / perturbed_inference_array.size
        )

        target_classes_properties = []
        target_classes_dropdown_options = []

        coverage_per_class: Dict[str, List[Union[str, float, int]]] = {}
        coverage_class_highlight: Dict[str, str] = {}

        # Iterate over the classes. Assign a color to them, create the dropdown
        # selector and prepare the coverage table.
        for i, target_class_name in enumerate(target_classes):

            color = f"#{class_colors[i][0]:02x}{class_colors[i][1]:02x}{class_colors[i][2]:02x}"
            target_classes_dropdown_options.append((target_class_name, i))

            if i in classes_in_inference:
                target_classes_properties.append(
                    {
                        "name": target_class_name,
                        "color": color,
                    }
                )

                coverage_per_class[target_class_name] = [
                    f"{coverage_original[i]:.2%}",
                    f"{coverage_perturbed[i]:.2%}",
                ]

                coverage_class_highlight[target_class_name] = color

        # All classes inference
        semantic_inference_widget = display_semantic_segmentation_inference_widget(
            original=observation,
            perturbed=perturbed_observation,
            original_prediction=inference_image,
            perturbed_prediction=perturbed_inference_image,
            target_classes=target_classes_properties,
        )

        # Coverage widget
        coverage_table = display_table(
            data=coverage_per_class,
            header=["Original", "Perturbed"],
            highlight_row_header=coverage_class_highlight,
            table_width=500,
        )
        percentage_of_pixels_that_changed_class = (
            np.count_nonzero(original_inference_array - perturbed_inference_array)
            / original_inference_array.size
        )

        coverage_widget = widgets.VBox(
            [
                coverage_table,
                widgets.HTML(
                    value="<b>Percentage of pixels with changed prediction</b>: "
                    f"{percentage_of_pixels_that_changed_class:.2%}"
                ),
            ]
        )

        # Metrics widget
        metrics_table_widget = display_table(
            data=self._get_metrics_for_id(perturbed_observation_id)
        )
        pipeline_info_table_widget = display_table(
            data=self._get_pipeline_info_for_id(perturbed_observation_id)
        )

        # Difference Widget
        difference_widget = display_static_observation_difference(
            original=observation, perturbed=perturbed_observation
        )

        view_elements = [
            semantic_inference_widget,
            coverage_widget,
            metrics_table_widget,
            pipeline_info_table_widget,
            difference_widget,
        ]
        view_element_headers = [
            "Model Inference",
            "Class Coverage",
            "Perturbation Size",
            "Perturbation Details",
            "Difference Between Original and Perturbed Observation",
        ]

        return self._assemble_widgets_in_view(
            observation_widget=observation_box_widget,
            widget_list=view_elements,
            widget_header=view_element_headers,
            warning_message=warning_message,
        )

    async def _get_object_detection_detail_view(
        self, perturbed_observation_id: int
    ) -> widgets.VBox:
        """
        Produce the object detection detail view for a given perturbed
        observation.

        :param perturbed_observation_id: ID specifying the perturbed
            observation.
        :raises ValueError: If the inference result type is not detection.
        :return: View as ipython widget.
        """
        artifact_details = await (
            PerturbedObservationDetails.get_by_perturbed_observation_id(
                perturbed_observation_id=perturbed_observation_id
            )
        )
        perturbed_observation: PIL.Image.Image = await (
            artifact_details.perturbed_observation_as_remote_file().fetch_remote_file()
        )
        observation_resource = await artifact_details.observation
        observation: PIL.Image.Image = (
            await observation_resource.as_remote_file().fetch_remote_file()
        )

        if not isinstance(
            artifact_details.observation_inference_result, ImageObjectDetectionModelOutput
        ) or not isinstance(
            artifact_details.perturbed_observation_inference_result, ImageObjectDetectionModelOutput
        ):
            raise ValueError("Model task is wrongly configured.")

        observation_inference = artifact_details.observation_inference_result.data
        perturbed_inference = artifact_details.perturbed_observation_inference_result.data

        class_names = artifact_details.inference_class_names
        n_classes = len(class_names)
        class_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in generate_color_list(n_classes)]

        observation_box_with_selector = display_selection_class_detection_widget(
            observation_image=observation,
            adversarial_example_image=perturbed_observation,
            observation_detection_output=observation_inference,
            adversarial_example_detection_output=perturbed_inference,
            class_names=class_names,
            class_colors=class_colors,
            observation_title="<center><b>Original Observation</b></center>",
            observation_caption=f"<center><b>ID</b>: {observation_resource.id}<br>"
            f"<b>File</b>: {observation_resource.name}</center>",
            perturbation_title="<center><b>Perturbed Observation</b></center>",
            perturbation_caption=f"<center><b>ID</b>: {perturbed_observation_id}</center>",
        )

        difference_widget = display_static_observation_difference(
            original=observation, perturbed=perturbed_observation
        )

        box_count_widget = display_object_detection_box_count_widget(
            original_detection_output=observation_inference,
            perturbed_detection_output=perturbed_inference,
            class_names=class_names,
            class_colors=class_colors,
        )
        metrics_table_widget = display_table(
            data=self._get_metrics_for_id(perturbed_observation_id)
        )
        pipeline_info_table_widget = display_table(
            data=self._get_pipeline_info_for_id(perturbed_observation_id)
        )

        warning_message = self._set_warning_message_if_target_class_not_in_original_inference(
            perturbed_observation_id,
            {prediction.class_index for prediction in observation_inference},
        )

        view_elements = [
            box_count_widget,
            metrics_table_widget,
            pipeline_info_table_widget,
            difference_widget,
        ]
        view_element_headers = [
            "Bounding Boxes per Class",
            "Perturbation Size",
            "Perturbation Details",
            "Difference Between Original and Perturbed Observation",
        ]

        return self._assemble_widgets_in_view(
            observation_widget=observation_box_with_selector,
            widget_list=view_elements,
            widget_header=view_element_headers,
            warning_message=warning_message,
        )

    async def get_detail_view(self, perturbed_observation_id: int) -> widgets.VBox:
        """
        Return the detail view for a given perturbation.

        This method automatically selects the view corresponding to the model task.

        :param perturbed_observation_id: ID specifying the perturbation.
        :raises ValueError: If invalid output type is passed.
        :return: View as ipython widget.
        """
        if self._data.report.output_type == OutputType.CLASSIFICATION:
            return await self._get_classification_detail_view(
                perturbed_observation_id=perturbed_observation_id
            )
        if self._data.report.output_type == OutputType.SEGMENTATION:
            return await self._get_semantic_segmentation_detail_view(
                perturbed_observation_id=perturbed_observation_id
            )
        if self._data.report.output_type == OutputType.DETECTION:
            return await self._get_object_detection_detail_view(
                perturbed_observation_id=perturbed_observation_id
            )

        raise ValueError(
            "Unsupported output type. Should be one of 'CLASSIFICATION', 'SEGMENTATION'\
                or 'DETECTION'."
        )
