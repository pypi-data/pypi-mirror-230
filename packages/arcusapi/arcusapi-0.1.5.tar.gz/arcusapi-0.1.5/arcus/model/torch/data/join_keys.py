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


import torch
from functorch import vmap


def index_of(row: torch.Tensor, tensor: torch.Tensor) -> int:
    """
    Returns the index of the first row in tensor that is equal to row.
    """
    row_present = (row == tensor).all(dim=-1)
    indices = torch.arange(len(tensor), dtype=torch.long)
    result = torch.where(
        row_present, indices, len(tensor) * torch.ones_like(indices)
    )
    return result.min()


def intersecting_row_indices(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """
    Returns which rows of y are present in x.
    """
    row_indices = vmap(index_of, in_dims=(0, None))(x, y)
    valid_row_indices = row_indices[row_indices < len(y)]
    return valid_row_indices


class JoinKeys:
    def __init__(self, keys: torch.Tensor):
        """
        JoinKeys are a 2D tensor of keys that are used to join two datasets.
        The first dimension is the batch dimension, and the second
        dimension is the number of keys. The keys are assumed to be unique.
        """
        self.keys = keys

    def __getitem__(self, index: int) -> torch.Tensor:
        return self.keys[index]

    def __len__(self):
        return len(self.keys)

    def get_keys(self) -> torch.Tensor:
        return self.keys

    def intersecting_indices(self, other) -> torch.Tensor:
        intersecting_rows = intersecting_row_indices(self.keys, other.keys)

        assert len(intersecting_rows) == len(
            self.keys
        ), "Missing keys when attempting to join keys."

        return intersecting_rows

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, JoinKeys):
            return False
        return torch.equal(self.get_keys(), __value.get_keys())
