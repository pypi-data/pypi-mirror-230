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
  Override Pytorch Lightning Trainer to add custom implementation of
  trial, fit, validate, test, predict, etc. to use the Arcus model consumer
  service API.
"""

import copy
from typing import Optional, Union

import pytorch_lightning as pl
from pytorch_lightning.utilities.types import (
    _EVALUATE_OUTPUT,
    _PREDICT_OUTPUT,
    EVAL_DATALOADERS,
    TRAIN_DATALOADERS,
)

from arcus.model.shared.data import CandidateMetadata, ProjectCandidateMetadata
from arcus.model.shared.trial import Trial
from arcus.model.torch.data import (
    TrainerDataLoaders,
    VerticalExternalDataClient,
    wrap_module_and_trainer_dataloaders_vertical,
)
from arcus.model.torch.metrics import ArcusMetricsCallback, Stage
from arcus.model.torch.utils import (
    configure_model_for_external,
    get_arcus_config,
    get_selection_metadata,
)

__all__ = [
    "Trainer",
]


class Trainer(pl.Trainer):
    def __init__(self, *args, **kwargs):
        """
        Override Pytorch Lightning Trainer to add custom implementation of
        trial, fit, validate, test, predict, etc. to use Arcus model
        enrichment.
        """

        # override callbacks to add an additional callback to report metrics
        callbacks = kwargs.pop("callbacks", [])
        self.reporting_callback = ArcusMetricsCallback()
        if isinstance(callbacks, list):
            callbacks.append(self.reporting_callback)
        else:
            callbacks = [callbacks, self.reporting_callback]
        kwargs["callbacks"] = callbacks

        super().__init__(*args, **kwargs)
        self.stage: Optional[Stage] = None
        self.latest_trial: Optional[Trial] = None
        self.candidate_metadata: Optional[CandidateMetadata] = None

    def _set_candidate_metadata(self, metadata: CandidateMetadata):
        self.candidate_metadata = metadata

    def get_candidate_metadata(self) -> Optional[CandidateMetadata]:
        return self.candidate_metadata

    def get_reporting_callback(self) -> ArcusMetricsCallback:
        return self.reporting_callback

    def get_stage(self) -> Optional[Stage]:
        return self.stage

    def get_latest_trial(self) -> Optional[Trial]:
        return self.latest_trial

    def _setup_arcus_loop(
        self,
        model: pl.LightningModule,
        original_dataloaders: TrainerDataLoaders,
        project_candidate_metadata: ProjectCandidateMetadata,
        datamodule: Optional[pl.LightningDataModule] = None,
        join_tensor_index: int = 0,
    ) -> TrainerDataLoaders:
        """
        Sets up the Arcus loop by wrapping the dataloaders and configuring
        the model for external data.
        """

        self._set_candidate_metadata(
            project_candidate_metadata.candidate_metadata
        )
        # Don't wrap data loaders if external data is not
        # being used.
        if not project_candidate_metadata.is_external():
            return original_dataloaders

        external_data_client = VerticalExternalDataClient(
            project_candidate_metadata=project_candidate_metadata,
        )

        wrapped_dataloaders = wrap_module_and_trainer_dataloaders_vertical(
            model,
            original_dataloaders,
            project_candidate_metadata.get_internal_join_column_indices(),
            datamodule,
            external_data_client,
            join_tensor_index,
        )

        configure_model_for_external(
            model,
            external_data_client,
        )

        return wrapped_dataloaders

    def trial(
        self,
        model: pl.LightningModule,
        train_dataloaders: Optional[
            Union[TRAIN_DATALOADERS, pl.LightningDataModule]
        ] = None,
        val_dataloaders: Optional[EVAL_DATALOADERS] = None,
        datamodule: Optional[pl.LightningDataModule] = None,
        ckpt_path: Optional[str] = None,
    ) -> Trial:
        """
        Runs a trial of matched data sources found by Arcus discovery service.
        """

        self.stage = Stage.TRIAL
        config = get_arcus_config(model)
        self.latest_trial = Trial(config)
        self.original_callbacks = self.callbacks

        for (
            candidate_candidate_id,
            candidate_data_metadata,
        ) in self.latest_trial.get_candidates_dict().items():
            curr_metadata = ProjectCandidateMetadata(
                config=config,
                candidate_metadata=candidate_data_metadata,
            )

            self.callbacks = [
                copy.deepcopy(callback)
                if not isinstance(callback, ArcusMetricsCallback)
                else callback
                for callback in self.original_callbacks
            ]

            self._train_val(
                copy.deepcopy(model),
                copy.deepcopy(train_dataloaders),
                copy.deepcopy(val_dataloaders),
                copy.deepcopy(datamodule),
                ckpt_path,
                curr_metadata,
            )

            # Resets epoch to 0
            self.fit_loop.epoch_progress.current.reset()
            self.fit_loop.epoch_progress.total.reset()
            self.should_stop = False

            # Ensures that the metrics from the final
            # epoch are reported
            self.get_reporting_callback().post_metrics()

            self.latest_trial.store_candidate_metrics(
                candidate_candidate_id,
                self.get_reporting_callback().get_metrics(),
            )

        self.latest_trial.complete()

        self.callbacks = self.original_callbacks
        return self.latest_trial

    def _train_val(
        self,
        model: pl.LightningModule,
        train_dataloaders: Optional[
            Union[TRAIN_DATALOADERS, pl.LightningDataModule]
        ] = None,
        val_dataloaders: Optional[EVAL_DATALOADERS] = None,
        datamodule: Optional[pl.LightningDataModule] = None,
        ckpt_path: Optional[str] = None,
        project_candidate_metadata: Optional[ProjectCandidateMetadata] = None,
        join_tensor_index: int = 0,
    ) -> None:
        if project_candidate_metadata is None:
            return super().fit(
                model,
                train_dataloaders,
                val_dataloaders,
                datamodule,
                ckpt_path,
            )

        curr_dataloaders = TrainerDataLoaders(
            train_dataloaders=train_dataloaders,
            val_dataloaders=val_dataloaders,
        )

        wrapped_dataloaders = self._setup_arcus_loop(
            model,
            curr_dataloaders,
            project_candidate_metadata,
            datamodule,
            join_tensor_index,
        )

        return super().fit(
            model,
            wrapped_dataloaders.get("train_dataloaders", None),
            wrapped_dataloaders.get("val_dataloaders", None),
            datamodule,
            ckpt_path,
        )

    def fit(
        self,
        model: pl.LightningModule,
        train_dataloaders: Optional[
            Union[TRAIN_DATALOADERS, pl.LightningDataModule]
        ] = None,
        val_dataloaders: Optional[EVAL_DATALOADERS] = None,
        datamodule: Optional[pl.LightningDataModule] = None,
        ckpt_path: Optional[str] = None,
    ) -> None:
        """
        Fits LightningModule using the given data loaders. Uses the Arcus model
        consumer service API to fetch external data.
        """

        self.stage = Stage.FIT

        project_candidate_metadata = get_selection_metadata(model)
        return self._train_val(
            model,
            train_dataloaders,
            val_dataloaders,
            datamodule,
            ckpt_path,
            project_candidate_metadata,
        )

    def validate(
        self,
        model: Optional[pl.LightningModule] = None,
        dataloaders: Optional[
            Union[EVAL_DATALOADERS, pl.LightningDataModule]
        ] = None,
        ckpt_path: Optional[str] = None,
        verbose: bool = True,
        datamodule: Optional[pl.LightningDataModule] = None,
    ) -> _EVALUATE_OUTPUT:
        """
        Runs validation using the given data loaders. Uses the Arcus model
        consumer service API to fetch external data.
        """
        self.stage = Stage.VALIDATE
        curr_dataloaders = TrainerDataLoaders(val_dataloaders=dataloaders)

        project_candidate_metadata = get_selection_metadata(model)
        wrapped_dataloaders = self._setup_arcus_loop(
            model,
            curr_dataloaders,
            project_candidate_metadata,
            datamodule,
        )

        return super().validate(
            model,
            wrapped_dataloaders.get("val_dataloaders", None),
            ckpt_path,
            verbose,
            datamodule,
        )

    def test(
        self,
        model: Optional[pl.LightningModule] = None,
        dataloaders: Optional[
            Union[EVAL_DATALOADERS, pl.LightningDataModule]
        ] = None,
        ckpt_path: Optional[str] = None,
        verbose: bool = True,
        datamodule: Optional[pl.LightningDataModule] = None,
    ) -> _EVALUATE_OUTPUT:
        """
        Runs test using the given data loaders. Uses the Arcus model
        consumer service API to fetch external data.
        """
        self.stage = Stage.TEST
        curr_dataloaders = TrainerDataLoaders(test_dataloaders=dataloaders)

        project_candidate_metadata = get_selection_metadata(model)
        wrapped_dataloaders = self._setup_arcus_loop(
            model,
            curr_dataloaders,
            project_candidate_metadata,
            datamodule,
        )

        return super().test(
            model,
            wrapped_dataloaders.get("test_dataloaders", None),
            ckpt_path,
            verbose,
            datamodule,
        )

    def predict(
        self,
        model: pl.LightningModule,
        dataloaders: Optional[
            Union[EVAL_DATALOADERS, pl.LightningDataModule]
        ] = None,
        datamodule: Optional[pl.LightningDataModule] = None,
        return_predictions: Optional[bool] = None,
        ckpt_path: Optional[str] = None,
    ) -> Optional[_PREDICT_OUTPUT]:
        """
        Runs prediction using the given data loaders. Uses the Arcus model
        consumer service API to fetch external data.
        """
        self.stage = Stage.PREDICT
        curr_dataloaders = TrainerDataLoaders(predict_dataloaders=dataloaders)

        project_candidate_metadata = get_selection_metadata(model)
        wrapped_dataloaders = self._setup_arcus_loop(
            model,
            curr_dataloaders,
            project_candidate_metadata,
            datamodule,
        )

        return super().predict(
            model,
            wrapped_dataloaders.get("predict_dataloaders", None),
            datamodule,
            return_predictions,
            ckpt_path,
        )
