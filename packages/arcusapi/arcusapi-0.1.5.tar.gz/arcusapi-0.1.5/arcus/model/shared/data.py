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


from enum import Enum
from typing import List

from arcus.model.shared.config import Config


class ExternalFeatureType(Enum):
    """
    Enum for the type of external data.
    """

    RAW = "RAW"
    EMBEDDING = "EMBEDDING"


class CandidateMetadata:
    def __init__(
        self,
        candidate_id: str,
        data_dim: int,
        join_column_indices: List[int],
        feature_type: ExternalFeatureType = ExternalFeatureType.RAW,
        is_external: bool = True,
    ):
        """
        Metadata for external data retrieved from Arcus. This is used to
        identify the external data and its type.
        """
        if is_external:
            assert (
                len(join_column_indices) > 0
            ), "Join column indices must be non-empty."

            assert (
                len(join_column_indices) <= data_dim
            ), "Number of join columns must be less than data dimension."

        self._is_external = is_external
        self.candidate_id = candidate_id
        self.data_dim = data_dim
        self.join_column_indices = join_column_indices
        self.feature_type = feature_type

    def is_external(self) -> bool:
        return self._is_external

    def get_candidate_id(self) -> str:
        return self.candidate_id

    def get_data_dim(self) -> int:
        return self.data_dim

    def get_feature_type(self) -> ExternalFeatureType:
        return self.feature_type

    def get_join_column_indices(self) -> List[int]:
        return self.join_column_indices


class ProjectCandidateMetadata:
    def __init__(
        self,
        config: Config,
        candidate_metadata: CandidateMetadata,
    ):
        """
        ProjectCandidateMetadata encapsulates both the project metadata and
        the candidate metadata. This is used to identify the external data
        and its type, as well as the project it belongs to and basic
        authentication information.
        """
        self.config = config
        self.candidate_metadata = candidate_metadata

        assertion_message = (
            "Candidate must have the same number of join columns "
            + "as the first-party data's join columns."
            + f" Candidate: {self.candidate_metadata.get_join_column_indices()}"
            + f" First-party: {self.config.get_join_column_indices()}"
        )

        if candidate_metadata.is_external():
            assert len(
                self.candidate_metadata.get_join_column_indices()
            ) == len(self.config.get_join_column_indices()), assertion_message

    def is_external(self) -> bool:
        return self.candidate_metadata.is_external()

    def get_candidate_id(self) -> str:
        return self.candidate_metadata.get_candidate_id()

    def get_data_dim(self) -> int:
        return self.candidate_metadata.get_data_dim()

    def get_feature_type(self) -> ExternalFeatureType:
        return self.candidate_metadata.get_feature_type()

    def get_api_key(self) -> str:
        return self.config.get_api_key()

    def get_project_id(self) -> str:
        return self.config.get_project_id()

    def get_config(self) -> Config:
        return self.config

    def get_external_join_column_indices(self) -> List[int]:
        return self.candidate_metadata.get_join_column_indices()

    def get_internal_join_column_indices(self) -> List[int]:
        return self.config.get_join_column_indices()
