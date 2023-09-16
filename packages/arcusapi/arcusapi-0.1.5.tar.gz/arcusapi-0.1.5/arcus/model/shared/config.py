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


from typing import List, Optional

from arcus.config import BaseConfig


class Config(BaseConfig):
    def __init__(
        self,
        api_key: str,
        project_id: str,
        input_dim: Optional[int] = None,
        output_dim: Optional[int] = None,
        column_headers: Optional[List[str]] = None,
        join_column_headers: Optional[List[str]] = None,
    ):
        """
        Configuration for a generic Arcus model.
        """

        super().__init__(api_key, project_id)

        if input_dim is not None:
            assert input_dim > 0, "Input dimension must be greater than 0"
        if output_dim is not None:
            assert output_dim > 0, "Output dimension must be greater than 0"

        self.input_dim = input_dim
        self.output_dim = output_dim
        self.column_headers = column_headers

        if self.column_headers is None or join_column_headers is None:
            self.join_column_indices = []
        else:
            self.join_column_indices = [
                self.column_headers.index(join_column)
                for join_column in join_column_headers
            ]

    def get_input_dim(self) -> Optional[int]:
        return self.input_dim

    def get_output_dim(self) -> Optional[int]:
        return self.output_dim

    def get_column_headers(self) -> List[str]:
        return self.column_headers

    def set_column_headers(self, column_headers: List[str]):
        self.column_headers = column_headers

    def get_join_column_indices(self) -> List[int]:
        return self.join_column_indices

    def set_join_column_headers(self, join_column_headers: List[str]):
        if self.column_headers is None:
            self.join_column_indices = []
        else:
            self.join_column_indices = [
                self.column_headers.index(join_column)
                for join_column in join_column_headers
            ]
