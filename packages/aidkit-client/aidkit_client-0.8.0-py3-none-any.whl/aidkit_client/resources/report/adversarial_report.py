"""
Resources for the Adversarial Report.
"""
from typing import Dict, List, Optional, Tuple, Union

import altair as alt
import pandas as pd
from pandas import DataFrame

from aidkit_client._endpoints.models import (
    ModelNormStats,
    ReportAdversarialResponse,
    ReportRequest,
)
from aidkit_client._endpoints.report import ReportAPI
from aidkit_client.aidkit_api import HTTPService
from aidkit_client.configuration import get_api_client
from aidkit_client.resources.dataset import Dataset, Subset
from aidkit_client.resources.ml_model import MLModelVersion
from aidkit_client.resources.report._base_report import _BaseReport


class AdversarialReport(_BaseReport):
    """
    A report which compares model versions.
    """

    _data: ReportAdversarialResponse

    def __init__(
        self, api_service: HTTPService, report_response: ReportAdversarialResponse
    ) -> None:
        """
        Create a new instance from the server response.

        :param api_service: Service instance to use for communicating with the
            server.
        :param report_response: Server response describing the report
            to be created.
        """
        self._data = report_response
        self._api_service = api_service
        self.model_id = None

    @classmethod
    async def get(
        cls,
        model_id: int,
        model_versions: List[Union[int, MLModelVersion]],
        dataset: Union[int, Dataset],
        subset: Union[int, Subset],
        metrics: Optional[List[str]] = None,
        success_metric_threshold: float = 0.7,
    ) -> "AdversarialReport":
        """
        Get the adversarial report to compare the given model versions.

        :param model_id: ID of the uploaded model of which versions are compared in the report.
        :param model_versions: List of model versions to compare in the report.
        :param dataset: Dataset to use for the comparison.
        :param subset: Subset whose observations are used for the comparison.
        :param metrics: List of distance metrics to consider in the comparison.
        :param success_metric_threshold: Threshold used to convert
                                        a success metric score to a binary success criterion.
        :return: Instance of the adversarial report.
        """
        if metrics is None:
            metrics = []
        model_version_ids = [
            model_version.id if isinstance(model_version, MLModelVersion) else model_version
            for model_version in model_versions
        ]
        dataset_id = dataset.id if isinstance(dataset, Dataset) else dataset
        subset_id = subset.id if isinstance(subset, Subset) else subset
        api_service = get_api_client()
        report = AdversarialReport(
            api_service=api_service,
            report_response=await ReportAPI(api_service).get_adversarial_report(
                request=ReportRequest(
                    model=model_id,
                    model_versions=model_version_ids,
                    dataset=dataset_id,
                    subset=subset_id,
                    metrics=metrics,
                    success_metric_threshold=success_metric_threshold,
                )
            ),
        )
        return report

    @staticmethod
    def _nested_dict_to_tuple_dict(
        nested_dict: Dict[str, Dict[str, Dict[str, ModelNormStats]]]
    ) -> Dict[Tuple[str, str, str], ModelNormStats]:
        return_dict: Dict[Tuple[str, str, str], ModelNormStats] = {}
        for index_1, dict_1 in nested_dict.items():
            for index_2, dict_2 in dict_1.items():
                for index_3, stats in dict_2.items():
                    return_dict[(index_1, index_2, index_3)] = stats
        return return_dict

    @classmethod
    def _get_summary_statistics(
        cls,
        stats_dict: Dict[
            str, Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, ModelNormStats]]]]]]
        ],
    ) -> DataFrame:
        # Open the nested dictionary in a dataframe.
        df = pd.json_normalize(stats_dict, sep="\u00AC")

        # Explode the columns so that every key from the dictionary is part of the index.
        df.columns = pd.MultiIndex.from_arrays(zip(*df.columns.str.split("\u00AC")))
        df = df.stack(level=0).droplevel(0)

        # Rearrange the dataframe to have the ODD Tag, Model Version, Mehtod and Parameters in the
        # row index.
        df = df.stack([0, 1, 2])

        def _f(x: Union[float, Tuple]) -> float:
            """
            Given either a float or a tuple containing a string and a float,
            flatten the tuple by only returning the float it contains.

            :param x: A float value or a (string, float) tuple with the string containing a
                description for the float.
            :return: Either the given float or the float from the (string, float) tuple.
            """
            if isinstance(x, float):
                return x

            return x[1]

        # Expand the ModelNormStats objects into multiple columns.
        df = df.apply(
            lambda x: x.apply(pd.Series)
            .stack()
            .rename({0: "impact", 1: "vulnerability", 2: "p_damage"}),
            axis=1,
        ).apply(lambda x: x.apply(_f))
        df.index.names = ("ODD Tag", "Model Version", "Method", "Parameters")
        return df

    def _fill_plot_with_data(self, plot: alt.LayerChart) -> alt.LayerChart:
        plot_copy = plot.copy(deep=True)
        plot_copy.data = self.data
        return plot_copy

    @property
    def summary_statistics(self) -> DataFrame:
        """
        Get the summary statistics for the report.

        :return: Pandas DataFrame containing statistics about the model robustness.
        """
        return self._get_summary_statistics(self._data.report.stats.summary_statistics)

    @property
    def model_comparison_plot(self) -> alt.LayerChart:
        """
        Get the model comparison plot of the report.

        :return: Altair chart that compares different model versions.
        """
        return self._fill_plot_with_data(
            alt.LayerChart.from_dict(self._data.report.plot_recipes.model_comparison_asr)
        )

    @property
    def attack_comparison_plot(self) -> alt.LayerChart:
        """
        Get the attack-comparison plot of the report.

        :return: Altair chart that compares different attacks.
        """
        return self._fill_plot_with_data(
            alt.LayerChart.from_dict(self._data.report.plot_recipes.attack_comparison_asr)
        )
