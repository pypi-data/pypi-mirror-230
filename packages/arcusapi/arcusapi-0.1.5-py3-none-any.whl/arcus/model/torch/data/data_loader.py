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


from typing import List, Optional, Sequence, Union

import torch
from torch.utils.data import DataLoader

from arcus.model.torch.data.data_client import VerticalExternalDataClient
from arcus.model.torch.data.dataset import VerticallyAugmentedDataset
from arcus.model.torch.data.join_keys import JoinKeys
from arcus.model.torch.data.tensor import (
    ExternalDataTensor,
    VerticallyAugmentedTensor,
)

__all__ = [
    "VerticallyAugmentedDataLoader",
    "wrap_dataloader_vertical",
]


class VerticallyAugmentedDataLoader(DataLoader):
    """
    A wrapper for a DataLoader that is vertically augmented with external
    data.

    Args:
        external_data_client: The client to use to fetch external data.
        internal_join_column_indices: The indices of the columns in the
            internal dataset to join with the external data.
        join_tensor_index: The index of the tensor in the internal dataset
            to join with the external data. This is used to handle when a
            DataLoader returns multiple tensors, and only one of them is
            to be joined with the external data.
        **kwargs: The arguments to pass to the DataLoader constructor.
    """

    def __init__(
        self,
        external_data_client: VerticalExternalDataClient,
        internal_join_column_indices: List[str],
        join_tensor_index: int = 0,
        **kwargs,
    ):
        assert (
            join_tensor_index >= 0
        ), "join_tensor_index must be non-negative."

        self.join_tensor_index = join_tensor_index
        self.internal_join_column_indices = internal_join_column_indices
        self.external_data_client = external_data_client

        if "dataset" not in kwargs:
            assert False, "Only Dataloaders with a dataset are supported."

        existing_dataset = kwargs.pop("dataset")

        assert "batch_sampler" in kwargs, (
            "Batch sampler must be present to initialize "
            + "a ArcusVerticalDataLoaderWrapper."
        )

        if isinstance(existing_dataset, VerticallyAugmentedDataset):
            dataset = existing_dataset
        else:
            dataset = VerticallyAugmentedDataset(
                existing_dataset,
                internal_join_column_indices,
                join_tensor_index,
            )

        # Get the relevant arguments from the DataLoader.
        relevant_kwargs = [
            "batch_sampler",
            "num_workers",
            "collate_fn",
            "pin_memory",
            "drop_last",
            "timeout",
            "worker_init_fn",
            "multiprocessing_context",
            "generator",
            "prefetch_factor",
            "persistent_workers",
            "pin_memory_device",
        ]

        kwargs = {k: v for k, v in kwargs.items() if k in relevant_kwargs}

        # initialize the dataloader with the wrapped dataset
        super().__init__(dataset, **kwargs)

    def get_dataset(self) -> VerticallyAugmentedDataset:
        return self.dataset

    def __iter__(self) -> Union[Sequence, VerticallyAugmentedTensor]:
        # Get the original batch iterator from the DataLoader
        batch_iterator = super().__iter__()

        for batch in batch_iterator:
            # this is set by the ArcusVerticalDatasetWrapper
            internal_batch, internal_join_keys_tensor = batch

            internal_join_keys = JoinKeys(internal_join_keys_tensor)

            # fetch the relevant external data
            # for now, this just takes the index
            external_batch: ExternalDataTensor = (
                self.external_data_client.fetch_batch(internal_join_keys)
            )

            # This object will augment the elements in the batch
            # with the retrieved external data. In the case that there
            # are many elements in the batch (e.g. data, labels), wraps the
            # self.join_tensor_index'th element and leaves the rest unchanged.
            batch_with_external_data = None

            if isinstance(internal_batch, Sequence):
                # join the self.join_tensor_index'th item of the internal batch
                # with the retrieved external data
                assert (
                    len(internal_batch) > 0
                ), "Internal batch must not be empty."
                assert len(internal_batch) > self.join_tensor_index, (
                    "Internal batch must have at least "
                    + f"{self.join_tensor_index + 1} elements."
                )
                assert isinstance(
                    internal_batch[self.join_tensor_index], torch.Tensor
                ), "Only joining on tensors is supported."

                batch_with_external_data = [
                    VerticallyAugmentedTensor(
                        internal_batch[i], external_batch
                    )
                    if i == self.join_tensor_index
                    else internal_batch[i]
                    for i in range(len(internal_batch))
                ]
            elif isinstance(internal_batch, torch.Tensor):
                # join the internal batch tensor with the retrieved
                # external data
                batch_with_external_data = VerticallyAugmentedTensor(
                    internal_batch, external_batch
                )
            else:
                assert False, f"Unsupported batch type {type(internal_batch)}."

            yield batch_with_external_data


def wrap_dataloader_vertical(
    dataloader: DataLoader,
    internal_join_column_indices: List[str],
    external_data_client: Optional[VerticalExternalDataClient] = None,
    join_tensor_index: int = 0,
) -> VerticallyAugmentedDataLoader:
    """
    Wraps a DataLoader with an ArcusVerticalDataLoaderWrapper.
    """
    if external_data_client is None or isinstance(
        dataloader, VerticallyAugmentedDataLoader
    ):
        return dataloader

    return VerticallyAugmentedDataLoader(
        external_data_client,
        internal_join_column_indices,
        join_tensor_index=join_tensor_index,
        **dataloader.__dict__,
    )
