# Copyright [2023] [Arcus Inc.]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
  Utility functions for running trials over the Arcus data exchange.
"""

from typing import Dict, List

from arcus.api_client import APIClient, ArcusResponse
from arcus.constants import ARCUS_WEB_URL
from arcus.model.shared.config import Config
from arcus.model.shared.data import CandidateMetadata, ExternalFeatureType
from arcus.model.shared.metrics import MetricType, StepMetrics

VISUALIZE_RESULTS_TEXT = "For more details, visit"
TRIAL_TABLE_TITLE = "Trial Results"


class Trial:
    def __init__(self, config: Config):
        """
        Base class for a trial. A trial is a single run of a model over
        a set of external data candidates.
        """

        self.config = config
        self.api_client = APIClient(config)

        self.candidates: List[CandidateMetadata] = self._generate_candidates()
        self.candidates_dict: Dict[str, CandidateMetadata] = {
            candidate.candidate_id: candidate for candidate in self.candidates
        }

        self.candidate_metrics: Dict[str, StepMetrics] = {}
        self._base_items_to_repr = [
            "External Data Candidate",
            "Features",
            "Epochs",
        ]

    def get_config(self) -> Config:
        """
        Returns the Arcus model config.
        """

        return self.config

    def _generate_candidates(self) -> List[CandidateMetadata]:
        """
        Generates the data candidates from the model consumer service.
        """

        response: ArcusResponse = self.api_client.request(
            "POST",
            "model/candidates/metadata",
            params={
                "project_id": self.config.get_project_id(),
            },
            json={
                "column_headers": self.config.get_column_headers(),
            },
        )

        if not response.status_ok:
            raise Exception(
                f"Failed to fetch candidates for trial: {response.data}."
            )

        candidates = [
            CandidateMetadata(
                candidate["candidate_id"],
                candidate["data_dim"],
                candidate["join_column_indices"],
                ExternalFeatureType(candidate["feature_type"]),
                candidate["is_external"],
            )
            for candidate in response.data["candidates"]
        ]
        if len(candidates) == 0:
            raise Exception("No candidates found for trial.")

        return candidates

    def complete(self):
        """
        Registers the trial as complete.
        """
        response: ArcusResponse = self.api_client.request(
            "POST",
            "model/trial/complete",
            params={
                "project_id": self.config.get_project_id(),
            },
        )

        if not response.status_ok:
            raise Exception(f"Failed to complete trial: {response.data}.")

    def get_candidates(self) -> List[CandidateMetadata]:
        """
        Returns the data candidates.
        """

        return self.candidates

    def get_candidates_dict(self) -> Dict[str, CandidateMetadata]:
        """
        Returns the data candidates.
        """

        return self.candidates_dict

    def store_candidate_metrics(
        self, candidate_id: str, metric: List[StepMetrics]
    ) -> None:
        """
        Stores the metrics from running a trial on an individual
         data candidate locally.
        """

        assert (
            candidate_id in self.candidates_dict.keys()
        ), f"Candidate ID {candidate_id} not found in candidates."

        self.candidate_metrics[candidate_id] = metric

    def get_candidate_metrics(self) -> Dict[str, List[StepMetrics]]:
        """
        Returns the metrics from running a trial on all data candidates.
        """

        return self.candidate_metrics

    def _construct_metrics_table(
        self,
        items_to_repr: List[str],
        metric_names: List[MetricType],
        candidate_metrics: Dict[str, List[StepMetrics]],
        candidates_dict: Dict[str, CandidateMetadata],
    ) -> str:
        """
        Constructs a table of metrics given a list of items to represent
        and a list of metric names.
        """
        max_column_lengths = [len(item) for item in items_to_repr]

        # store rows
        rows = []
        for candidate_id, metrics in candidate_metrics.items():
            last_logged_metric: StepMetrics = metrics[-1]
            metrics_map: Dict[
                MetricType, float
            ] = last_logged_metric.get_metrics()

            candidate_metadata = candidates_dict[candidate_id]
            candidate_dim = (
                candidate_metadata.get_data_dim()
                if candidate_metadata.is_external()
                else "n/a"
            )
            row = [candidate_id, candidate_dim, len(metrics)]
            for metric_name in metric_names:
                row.append(metrics_map[metric_name])

            # update max column lengths
            for i, item in enumerate(row):
                max_column_lengths[i] = max(
                    max_column_lengths[i], len(str(item))
                )

            rows.append(row)

        # print rows, padding with spaces to match max column length
        rows_str = []
        for row in rows:
            row_str = []
            for i, item in enumerate(row):
                item_str = str(item)
                before_item_padding = " " * (
                    (max_column_lengths[i] - len(item_str)) // 2
                )
                after_item_padding = " " * (
                    max_column_lengths[i]
                    - len(item_str)
                    - len(before_item_padding)
                )
                item_str = before_item_padding + item_str + after_item_padding
                row_str.append(item_str)
            row_str = " | ".join(row_str)
            row_str = f"| {row_str} |"
            rows_str.append(row_str)

        # print header, padding with spaces to match max column length
        header_str = []
        for i, item in enumerate(items_to_repr):
            before_item_padding = " " * (
                (max_column_lengths[i] - len(item)) // 2
            )
            after_item_padding = " " * (
                max_column_lengths[i] - len(item) - len(before_item_padding)
            )
            item = before_item_padding + item + after_item_padding
            header_str.append(item)
        header = " | ".join(header_str)
        header = f"| {header} |"

        # print separator, padding with dashes to match max column length
        separator_str = []
        for i, item in enumerate(items_to_repr):
            separator_str.append("-" * max_column_lengths[i])
        separator = " | ".join(separator_str)
        separator = f"| {separator} |"

        # print title, centering over the whole table
        before_text_padding = " " * (
            (len(header) - len(TRIAL_TABLE_TITLE)) // 2
        )

        after_text_padding = " " * (
            len(header) - len(TRIAL_TABLE_TITLE) - len(before_text_padding)
        )

        metrics_table_title = (
            before_text_padding + TRIAL_TABLE_TITLE + after_text_padding
        )

        rows_str = "\n".join(rows_str)
        return f"{metrics_table_title}\n\n{header}\n{separator}\n{rows_str}"

    def summary(self) -> str:
        """
        Returns a summary of the trial in string format.
        The grid columns are:
            - candidate_id
            - number of added features
            - number of epochs
            - final validation accuracy (if present)
            - final validation loss (if present)
        """
        if len(self.candidate_metrics) == 0:
            return ""

        first_metrics: List[StepMetrics] = self.candidate_metrics[
            list(self.candidate_metrics.keys())[0]
        ]
        if len(first_metrics) == 0:
            return ""

        last_logged_first_metric: StepMetrics = first_metrics[-1]
        metrics_map: Dict[
            MetricType, float
        ] = last_logged_first_metric.get_metrics()
        if len(metrics_map) == 0:
            return ""

        metric_names: List[MetricType] = list(metrics_map.keys())
        metric_names_str: List[str] = [k.value for k in metric_names]
        items_to_repr = self._base_items_to_repr + metric_names_str

        metrics_table = self._construct_metrics_table(
            items_to_repr,
            metric_names,
            self.candidate_metrics,
            self.candidates_dict,
        )

        visualize_results_link = (
            f"{ARCUS_WEB_URL}/project/{self.config.get_project_id()}/"
        )

        # return metrics table with a link to visualize results
        return (
            f"{metrics_table}\n"
            + f"\n{VISUALIZE_RESULTS_TEXT} {visualize_results_link}."
        )

    def select(self, candidate_id: str) -> None:
        """
        Selects a candidate that was trialed for the project.
        """
        assert (
            candidate_id in self.candidates_dict.keys()
        ), f"Candidate ID {candidate_id} not found in candidates."

        response: ArcusResponse = self.api_client.request(
            "POST",
            "model/selections",
            params={
                "project_id": self.config.get_project_id(),
                "candidate_id": candidate_id,
            },
        )

        if not response.status_ok:
            raise Exception(
                f"Failed to make selection for project: {response.data}."
            )

        print(f"Selected candidate {candidate_id}.")
