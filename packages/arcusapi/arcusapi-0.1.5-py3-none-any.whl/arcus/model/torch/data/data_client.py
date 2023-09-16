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


from typing import Optional

import torch

from arcus.api_client import APIClient, ArcusResponse
from arcus.model.shared.config import Config
from arcus.model.shared.data import (
    ExternalFeatureType,
    ProjectCandidateMetadata,
)
from arcus.model.torch.data.join_keys import JoinKeys
from arcus.model.torch.data.tensor import ExternalDataTensor


class VerticalExternalDataClient:
    """
    Client for fetching external data from Arcus to vertically (i.e.
    feature-wise) augment first-party data passed.

    Args:
        project_candidate_metadata: ProjectCandidateMetadata object
            containing information about the project and candidate.
    """

    def __init__(
        self,
        project_candidate_metadata: ProjectCandidateMetadata,
    ):
        # TODO (CLI-98): external_data should be a data structure that
        # caches external data for certain join keys, rather than storing
        # the entire external data tensor.
        self.external_data: Optional[ExternalDataTensor] = None
        self.project_candidate_metadata = project_candidate_metadata

        self.external_data_dim: int = project_candidate_metadata.get_data_dim()
        self.feature_type: ExternalFeatureType = (
            project_candidate_metadata.get_feature_type()
        )
        self.candidate_id: str = project_candidate_metadata.get_candidate_id()

        self.config: Config = project_candidate_metadata.get_config()
        self.api_client = APIClient(self.config)

        self.external_join_column_indices = (
            self.project_candidate_metadata.get_external_join_column_indices()
        )

    def _fetch_external_data(
        self,
    ) -> ExternalDataTensor:
        # TODO (CLI-98): Pass join keys to Arcus API rather than
        #  fetching all external data and then joining.
        response: ArcusResponse = self.api_client.request(
            "GET",
            "model/data/features",
            params={
                "project_id": self.config.get_project_id(),
                "candidate_id": self.candidate_id,
            },
        )

        if not response.status_ok:
            raise Exception("Unable to fetch external data from Arcus.")

        external_data_tensor: torch.Tensor = torch.tensor(
            response.data["data"], dtype=torch.float32
        )

        assert (
            len(external_data_tensor.shape) == 2
        ), "External data must be 2-dimensional."

        assert self.external_data_dim == (
            external_data_tensor.shape[1]
            - len(self.external_join_column_indices)
        ), (
            "External data must have the same number of "
            + "dimensions as the model expects. "
            + f"Expected {self.external_data_dim}, got "
            + str(
                external_data_tensor.shape[1]
                - len(self.external_join_column_indices)
            )
            + "."
        )
        return ExternalDataTensor(external_data_tensor, self.feature_type)

    def fetch_batch(
        self,
        internal_join_keys: JoinKeys,
    ) -> ExternalDataTensor:
        """
        Fetch a batch of external data from Arcus.
        Args:
            join_keys: A list of join keys to fetch external data for.
        Returns:
            A batch of external data, as an ExternalDataTensor.
        """

        # TODO (CLI-98): Pass join keys to Arcus API rather than
        #  fetching all external data and then joining.
        if self.external_data is None:
            self.external_data = self._fetch_external_data()

        external_join_keys = JoinKeys(
            self.external_data.get_data()[:, self.external_join_column_indices]
        )

        external_data_row_indices = internal_join_keys.intersecting_indices(
            external_join_keys
        )

        external_data_without_join_columns = self.external_data[
            :,
            [
                i
                for i in range(self.external_data.shape[1])
                if i not in self.external_join_column_indices
            ],
        ]

        return external_data_without_join_columns[external_data_row_indices]

    def __len__(self):
        if self.external_data is None:
            return 0
        return len(self.external_data)

    def __repr__(self):
        return (
            f"Arcus {self.feature_type} data with "
            + f"{self.external_data_dim} dimensions."
        )

    def __str__(self) -> str:
        return self.__repr__()

    def is_raw(self) -> bool:
        return self.feature_type is ExternalFeatureType.RAW

    def is_embedding(self) -> bool:
        return self.feature_type is ExternalFeatureType.EMBEDDING

    @property
    def shape(self) -> torch.Size:
        return torch.Size([len(self), self.external_data_dim])

    def get_external_data_dim(self) -> int:
        return self.external_data_dim

    def get_feature_type(self) -> ExternalFeatureType:
        return self.feature_type
