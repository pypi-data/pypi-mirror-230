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


from typing import List, Sequence

import torch
from torch.utils.data import Dataset


class VerticallyAugmentedDataset(Dataset):
    def __init__(
        self,
        first_party_dataset: Dataset,
        join_column_indices: List[int],
        join_tensor_index: int = 0,
    ):
        """
        A wrapper for a Dataset that provides first-party data. Adds additional
        information to the batch returned by the internal dataset, which
        provides necessary context for `ArcusVerticalDataLoaderWrapper` to
        fetch the relevant external data.

        Args:
            first_party_dataset: The first-party dataset to wrap.
            join_column_indices: The indices of the columns in the internal
                dataset to join with the external data.
            join_tensor_index: The index of the tensor in the internal dataset
                to join with the external data. This is used to handle when a
                DataLoader returns multiple tensors, and only one of them is
                to be joined with the external data.

        __getitem__ adds the join keys from the internal dataset to the batch.
        """

        if isinstance(first_party_dataset, VerticallyAugmentedDataset):
            assert False, "VerticalDatasetWrapper cannot be nested."

        self.first_party_dataset = first_party_dataset
        self.join_column_indices = join_column_indices
        self.join_tensor_index = join_tensor_index

        super().__init__()

    # Keep all existing methods of self.first_party_dataset except those
    # overriden here.
    def __getattr__(self, attr):
        if hasattr(self.first_party_dataset, attr):
            return getattr(self.first_party_dataset, attr)

        raise AttributeError(f"Attribute {attr} not found.")

    def __getitem__(self, index: int):
        internal_batch = self.first_party_dataset[index]
        internal_batch_tensor = internal_batch

        if isinstance(internal_batch, Sequence):
            # join the self.join_tensor_index'th item of the internal batch
            # with the retrieved external data
            assert len(internal_batch) > 0, "Internal batch must not be empty."
            assert len(internal_batch) > self.join_tensor_index, (
                "Internal batch must have at least "
                + f"{self.join_tensor_index + 1} elements."
            )
            assert isinstance(
                internal_batch[self.join_tensor_index], torch.Tensor
            ), "Only joining on tensors is supported."

            internal_batch_tensor = internal_batch[self.join_tensor_index]

        if len(internal_batch_tensor.shape) == 1:
            join_keys = internal_batch_tensor[self.join_column_indices]
        else:
            join_keys = internal_batch_tensor[:, self.join_column_indices]

        return internal_batch, join_keys

    def __len__(self):
        return len(self.first_party_dataset)
