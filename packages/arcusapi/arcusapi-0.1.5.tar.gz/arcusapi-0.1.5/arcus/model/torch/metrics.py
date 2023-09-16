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
from typing import Dict, List, Optional

from pytorch_lightning import Callback, LightningModule, Trainer

from arcus.constants import ARCUS_MODULE_NAME
from arcus.model.shared.config import Config
from arcus.model.shared.metrics import (
    SUPPORTED_METRICS,
    MetricStore,
    Stage,
    StepMetrics,
)
from arcus.model.torch.utils import get_arcus_config

logger = logging.getLogger(ARCUS_MODULE_NAME)


class ArcusMetricsCallback(Callback):
    def __init__(
        self,
        metric_names: List[str] = SUPPORTED_METRICS,
    ):
        """
        A PyTorch Lightning callback that reports metrics to Arcus at the end
        of each validation epoch.
        """
        super(ArcusMetricsCallback, self).__init__()
        self.metric_names = metric_names
        self.metric_store = None

    def setup(
        self, trainer: Trainer, pl_module: LightningModule, stage: str
    ) -> None:
        # Initialize a new metric store every time
        # `trial, fit, validate, test, predict` is called.
        # Don't use the passed-in stage, since it does not have concept of
        # trial.
        try:
            trainer_stage: Optional[Stage] = trainer.get_stage()
            candidate_metadata = trainer.get_candidate_metadata()
        except AttributeError:
            raise ValueError(
                "ArcusMetricsCallback must be used with ArcusTrainer."
            )

        model_config: Config = get_arcus_config(pl_module)
        self.metric_store = MetricStore(
            model_config,
            candidate_metadata,
            self.metric_names,
            trainer_stage,
        )

    def on_validation_epoch_end(
        self, trainer: Trainer, pl_module: LightningModule
    ):
        # Don't report if just doing initial validation sanity checks.
        if trainer.sanity_checking:
            return

        callback_metrics_float: Dict[str, float] = {
            k: v.item() for k, v in trainer.callback_metrics.items()
        }
        should_stop = self.metric_store.log(callback_metrics_float)

        should_stop = trainer.strategy.reduce_boolean_decision(
            should_stop, all=False
        )

        # This value is used by the torch _run_early_stopping_check,
        # https://pytorch-lightning.readthedocs.io/en/1.4.9/_modules/pytorch_lightning/callbacks/early_stopping.html
        trainer.should_stop = trainer.should_stop or should_stop
        if should_stop:
            logger.info("Arcus is stopping training early.")

    def get_metrics(self) -> Optional[List[StepMetrics]]:
        if self.metric_store is None:
            return None
        return self.metric_store.get()

    def post_metrics(self) -> None:
        if self.metric_store is None:
            return None
        self.metric_store.post_metrics()
