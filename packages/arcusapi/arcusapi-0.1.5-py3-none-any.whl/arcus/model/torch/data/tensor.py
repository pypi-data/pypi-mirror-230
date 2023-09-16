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


from typing import List, Optional, Union

import torch

from arcus.model.shared.data import ExternalFeatureType


class ExternalDataTensor:
    """
    Represents a tensor that is obtained from the Arcus data exchange.
    Args:
        external_data_values: The values of the data that is obtained from
            the Arcus data exchange.
        feature_type: The type of the external data (raw or embeddings).
    """

    def __init__(
        self,
        external_data_values: torch.Tensor,
        feature_type: Optional[ExternalFeatureType] = ExternalFeatureType.RAW,
    ):
        """
        Represents a tensor that is obtained from the Arcus data exchange.
        """
        self.external_data_values = external_data_values
        self.feature_type = feature_type

    def __len__(self):
        return len(self.external_data_values)

    @property
    def shape(self):
        return self.external_data_values.shape

    def __getitem__(self, index: Union[int, List[int], slice, torch.Tensor]):
        return ExternalDataTensor(
            self.external_data_values[index],
            self.feature_type,
        )

    def is_raw(self) -> bool:
        return self.feature_type is ExternalFeatureType.RAW

    def is_embedding(self) -> bool:
        return self.feature_type is ExternalFeatureType.EMBEDDING

    def get_data(self) -> torch.Tensor:
        return self.external_data_values


class VerticallyAugmentedTensor:
    """
    Represents a tensor that is vertically augmented with external data
        from the Arcus Data Exchange.
    Args:
        first_party_data: The first party data.
        external_data: The external data.
    """

    def __init__(
        self,
        first_party_data: torch.Tensor,
        external_data: ExternalDataTensor,
    ):
        assert len(first_party_data) == len(
            external_data
        ), "Internal and external data must have the same number of samples."

        self.first_party_data = first_party_data
        self.external_data = external_data

    def __len__(self) -> int:
        return len(self.first_party_data)

    def get_first_party_data(self) -> torch.Tensor:
        return self.first_party_data

    def get_external_data(self) -> ExternalDataTensor:
        return self.external_data
