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
from typing import Optional

import pytorch_lightning as pl

from arcus.api_client import APIClient, ArcusResponse
from arcus.constants import ARCUS_MODULE_NAME
from arcus.model.shared.config import Config
from arcus.model.shared.data import (
    CandidateMetadata,
    ExternalFeatureType,
    ProjectCandidateMetadata,
)
from arcus.model.torch.data import VerticalExternalDataClient
from arcus.model.torch.model import EmbeddingType, HeadType

logger = logging.getLogger(ARCUS_MODULE_NAME)

__all__ = [
    "get_arcus_config",
    "get_selection_metadata",
    "configure_model_for_external",
]


def get_arcus_config(
    model: pl.LightningModule,
) -> Config:
    try:
        return model.model.get_config()
    except AttributeError:
        assert False, (
            "LightningModule without model attribute does "
            + "not support external data"
        )


def get_selection_metadata(
    model: pl.LightningModule,
) -> Optional[ProjectCandidateMetadata]:
    """
    Gets the Arcus metadata of the selction for the given model using the
    Arcus API.
    """
    config = get_arcus_config(model)
    api_client = APIClient(config)

    response: ArcusResponse = api_client.request(
        "GET",
        "model/selections/metadata",
        params={"project_id": config.get_project_id()},
    )

    if not response.status_ok:
        raise RuntimeError(
            "Failed to retrieve data selection. Make sure a selection has "
            + "been made for this project."
        )
        return None

    response_data = response.data

    candidate_metadata = CandidateMetadata(
        candidate_id=response_data["candidate_id"],
        data_dim=response_data["data_dim"],
        join_column_indices=response_data["join_column_indices"],
        feature_type=ExternalFeatureType(response_data["feature_type"]),
        is_external=response_data["is_external"],
    )

    return ProjectCandidateMetadata(
        config=config,
        candidate_metadata=candidate_metadata,
    )


def configure_model_for_external(
    model: pl.LightningModule,
    external_data_client: Optional[VerticalExternalDataClient] = None,
    head_type: HeadType = HeadType.MLP,
    embedding_type: EmbeddingType = EmbeddingType.MLP,
    embedding_depth: int = 3,
    embedding_dim: int = 128,
) -> None:
    """
    Configures the given model to use external data.
    """
    if external_data_client is None:
        return

    external_data_dim = external_data_client.get_external_data_dim()
    external_data_type = external_data_client.get_feature_type()
    try:
        if external_data_client.is_raw():
            model.model.configure_for_external_raw(
                external_data_dim,
                embedding_dim,
                embedding_type,
                head_type,
                embedding_depth,
            )
        elif external_data_client.is_embedding():
            model.model.configure_for_external_embeddings(
                external_data_dim, head_type
            )
        else:
            assert (
                False
            ), f"External data type {external_data_type} not suppported"
    except AttributeError:
        assert False, (
            "LightningModule without model attribute does "
            + "not support external data"
        )
