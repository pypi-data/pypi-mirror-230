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


import logging
import time
from enum import Enum
from typing import Dict, List

from arcus.api_client import APIClient, ArcusResponse
from arcus.constants import ARCUS_MODULE_NAME
from arcus.model.shared.config import Config
from arcus.model.shared.data import CandidateMetadata

logger = logging.getLogger(ARCUS_MODULE_NAME)


class MetricType(Enum):
    """
    Enum for the types of metrics. These are what you can log in your model
    to report important metrics to Arcus. This enum is used to enumerate the
    types of metrics that Arcus can track.
    """

    VAL_ACCURACY = "val_accuracy"
    VAL_LOSS = "val_loss"


class Stage(Enum):
    """
    Stage of the model lifecycle. This is used when logging metrics
    to Arcus.
    """

    TRIAL = "trial"
    FIT = "fit"
    VALIDATE = "validate"
    TEST = "test"
    PREDICT = "predict"


# The list of the names of metrics that can be logged to Arcus.
SUPPORTED_METRICS: List[str] = [e.value for e in MetricType]
LOG_EVERY_N_STEPS = 5


class StepMetrics:
    def __init__(
        self,
        metrics_map: Dict[MetricType, float],
    ):
        """
        StepMetrics encodes the metrics for a single step (epoch) of the model.
        """
        self.timestamp = time.time()
        self.metrics_map = metrics_map

    def get_metrics(self) -> Dict[MetricType, float]:
        return self.metrics_map

    def get_metrics_string(self) -> Dict[str, float]:
        # convert metric keys to strings rather than enum
        return {k.value: v for k, v in self.metrics_map.items()}

    def get_timestamp(self) -> float:
        return self.timestamp


class MetricStore:
    def __init__(
        self,
        config: Config,
        candidate_metadata: CandidateMetadata,
        metric_names: List[str] = SUPPORTED_METRICS,
        stage: Stage = Stage.FIT,
    ):
        """
        MetricStore is used to store the metrics for a single data candidate.
        It is used to log the metrics to Arcus.
        """
        self.stage = stage

        self.config = config
        self.candidate_metadata = candidate_metadata
        self.metric_names = []

        for metric_name in metric_names:
            if metric_name in SUPPORTED_METRICS:
                self.metric_names.append(metric_name)
            else:
                logger.warning(
                    f"Metric {metric_name} is not a valid metric type,"
                    + " will not be logged."
                )
        self.empty_warning_disabled = False

        # Metrics are stored as a list, where each element is a StepMetrics
        # object. Each element represents the metrics for a single step.
        self.metrics: List[StepMetrics] = []

        self.api_client = APIClient(config)

    def log(self, logged_metrics: Dict[str, float]) -> bool:
        report_dict = {}

        for metric in self.metric_names:
            if metric in logged_metrics:
                metric_value = logged_metrics[metric]

                if not isinstance(metric_value, float):
                    logger.warning(
                        f"Metric {metric} is not a float, will not "
                        + "be logged."
                    )
                else:
                    report_dict[MetricType(metric)] = metric_value

        if len(report_dict) == 0:
            if not self.empty_warning_disabled:
                logger.warning(
                    "No metrics are being logged to Arcus. Supported"
                    + f" metrics are: {SUPPORTED_METRICS}. Log these"
                    + " metrics to ensure they are logged to Arcus."
                )
                self.empty_warning_disabled = True

            return

        self.metrics.append(StepMetrics(report_dict))

        should_stop = False
        if (
            len(self.metrics) == 1
            or len(self.metrics) % LOG_EVERY_N_STEPS == 0
        ):
            should_stop = self.post_metrics()
        return should_stop

    def get(self) -> List[StepMetrics]:
        return self.metrics

    def get_string(self) -> List[Dict[str, float]]:
        return [m.get_metrics_string() for m in self.metrics]

    def get_metric_names(self) -> List[str]:
        return self.metric_names

    def get_stage(self) -> Stage:
        return self.stage

    def get_config(self) -> Config:
        return self.config

    def get_candidate_metadata(self) -> CandidateMetadata:
        return self.candidate_metadata

    def post_metrics(self) -> bool:
        """
        Post the metrics to Arcus. Returns True if the model training should be
        early-stopped, False otherwise.
        """
        should_early_stop = False

        response: ArcusResponse = self.api_client.request(
            "POST",
            "model/metrics",
            params={
                "project_id": self.config.get_project_id(),
                "stage": self.stage.value,
                "candidate_id": self.candidate_metadata.get_candidate_id(),
                "num_epochs": len(self.get()),
            },
            json={"metrics": self.get_string()},
        )

        if not response.status_ok:
            logger.warning("Failed to post metrics to Arcus.")
            return False

        should_early_stop = response.data["should_early_stop"]
        return should_early_stop
