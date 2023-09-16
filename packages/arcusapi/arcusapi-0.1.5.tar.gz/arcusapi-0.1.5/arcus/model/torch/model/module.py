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


from typing import Callable, Optional, Union

import torch

from arcus.model.shared import Config
from arcus.model.torch import ExternalDataTensor, VerticallyAugmentedTensor
from arcus.model.torch.model.embedding_getter import EmbeddingGetter
from arcus.model.torch.model.model_types import EmbeddingType, HeadType
from arcus.model.torch.model.utils import get_embed_dim, get_output_dim

MLP_WIDTH_MULTIPLIER = 2


class Model(torch.nn.Module):
    """
    A decorator class of torch.nn.Module which takes
    a torch.nn.Module as input and overrides it to add
    functionality to its forward pass.
    """

    def __init__(
        self,
        module: torch.nn.Module,
        config: Config,
        embed_fn: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        input_dim: Optional[int] = None,
    ):
        super(Model, self).__init__()
        self.config = config

        if input_dim is None:
            input_dim = config.get_input_dim()
            if input_dim is None:
                try:
                    input_dim = module.input_dim
                except AttributeError:
                    raise ValueError(
                        "input_dim must be specified, either in the config"
                        + "or as an argument to arcus.model.torch.Model"
                    )

        assert input_dim > 0, "input_dim must be greater than 0"
        assert isinstance(input_dim, int), "input_dim must be an integer"

        if embed_fn is None:
            embed_fn = EmbeddingGetter(module)

        self.first_party_embedding_fn = embed_fn
        self.first_party_embedding_dim = get_embed_dim(
            embed_fn,
            input_dim,
        )

        if config.get_output_dim() is None:
            self.output_dim = get_output_dim(module, input_dim)
        else:
            self.output_dim = config.get_output_dim()

        column_headers = config.get_column_headers()
        if column_headers is None:
            try:
                column_headers = module.column_headers
                config.set_column_headers(column_headers)
            except AttributeError:
                pass

        join_column_indices = config.get_join_column_indices()
        if len(join_column_indices) == 0:
            try:
                join_column_headers = module.join_column_headers
                config.set_join_column_headers(join_column_headers)
            except AttributeError:
                pass

        self.module = module
        self.external_data_dim = 0
        self.external_embedding_dim = 0
        self.head_module = None
        self.external_embedding_module = None

        self.configured = False

    def get_config(self) -> Config:
        """
        Returns the config of the model.
        """
        return self.config

    def is_configured(self) -> bool:
        """
        Returns whether the model has been configured.
        """
        return self.configured

    def get_head_module(self) -> Optional[torch.nn.Module]:
        """
        Returns the head module of the model.
        """
        return self.head_module

    def get_external_embedding_module(self) -> Optional[torch.nn.Module]:
        """
        Returns the external embedding module of the model.
        """
        return self.external_embedding_module

    def get_external_embedding_dim(self) -> int:
        """
        Returns the dimension of the external data embedding.
        """
        return self.external_embedding_dim

    def get_external_data_dim(self) -> int:
        """
        Returns the dimension of the external data.
        """
        return self.external_data_dim

    def configure_for_external_embeddings(
        self,
        external_data_embedding_dim: int,
        head_type: HeadType = HeadType.MLP,
    ):
        """
        Configures the model to use external data embeddings.
        Creates the head of the module to merge first-party and external
        emebeddings.
        Args:
            external_data_embedding_dim: The dimension of the desired
                external data embedding
            head_type: The type of head to use.
                Currently only linear and mlp are supported.
        """
        if not self.configured:
            self._configure_head(external_data_embedding_dim, head_type)
            self.configured = True

    def configure_for_external_raw(
        self,
        external_data_dim: int,
        external_data_embedding_dim: int,
        embedding_type: EmbeddingType = EmbeddingType.MLP,
        head_type: HeadType = HeadType.MLP,
        embedding_depth: int = 3,
    ):
        """
        Configures the model to use external raw data.
        Creates embedding module to map raw external data to embedding space,
        then configures the head of the model.
        Args:
            external_data_dim: The dimension of the external data
            external_data_embedding_dim: The dimension of the desired
                external data embedding
            embedding_type: The type of embedding to use.
                Currently only linear and mlp are supported.
            head_type: The type of head to use.
                Currently only linear and mlp are supported.
            embedding_depth: The number of layers in the embedding
        """
        if not self.configured:
            self._configure_external_embedding(
                external_data_dim,
                external_data_embedding_dim,
                embedding_type,
                embedding_depth,
            )
            self._configure_head(external_data_embedding_dim, head_type)
            self.configured = True

    def _configure_head(
        self, external_embedding_dim: int, head_type: HeadType = HeadType.MLP
    ):
        """
        Configures the head of the model.
        Args:
          external_data_embedding_dim: The dimension of the external
            data embedding.
          head_type: The type of head to use.
            Currently only linear and mlp are supported.
        """
        self.external_embedding_dim = external_embedding_dim
        self.head_module = self._head_from_type(
            head_type,
            self.first_party_embedding_dim,
            external_embedding_dim,
            self.output_dim,
        )

    def _configure_external_embedding(
        self,
        external_data_dim: int,
        external_data_embedding_dim: int,
        embedding_type: HeadType = HeadType.MLP,
        embedding_depth: int = 3,
    ):
        """
        Configures the embedding for external data passed to the model.
        Args:
            external_data_dim: The dimension of the external data
            external_data_embedding_dim: The dimension of the desired
                external data embedding
            embedding_type: The type of embedding to use.
                Currently only linear and mlp are supported.
            embedding_depth: The number of layers in the embedding
        """

        # first-party data dimension
        self.external_data_dim = external_data_dim
        self.external_embedding_dim = external_data_embedding_dim
        self.external_embedding_module = self._embedding_from_type(
            embedding_type,
            external_data_dim,
            external_data_embedding_dim,
            embedding_depth,
        )

    def _embedding_from_type(
        self,
        embedding_type: EmbeddingType,
        external_data_dim: int,
        external_data_embedding_dim: int,
        embedding_depth: int,
    ) -> torch.nn.Module:
        """
        Returns an embedding of external data from given type.
        Args:
            embedding_type: The type of embedding to use.
                Currently only linear and mlp are supported.
            external_data_dim: The dimension of the external data
            external_data_embedding_dim: The dimension of the desired
                external data embedding
            embedding_depth: The number of layers in the embedding
        """
        if embedding_type is EmbeddingType.LINEAR:
            first_layer = torch.nn.Linear(
                external_data_dim, external_data_embedding_dim
            )
            remaining_layers = [
                torch.nn.Linear(
                    external_data_embedding_dim, external_data_embedding_dim
                )
                for _ in range(embedding_depth - 1)
            ]

            return torch.nn.Sequential(first_layer, *remaining_layers)
        elif embedding_type is EmbeddingType.MLP:
            first_layer = torch.nn.Linear(
                external_data_dim, external_data_embedding_dim
            )
            remaining_layers = [
                torch.nn.Sequential(
                    torch.nn.Linear(
                        external_data_embedding_dim,
                        external_data_embedding_dim,
                    ),
                    torch.nn.ReLU(),
                )
                for _ in range(embedding_depth - 1)
            ]

            return torch.nn.Sequential(first_layer, *remaining_layers)
        else:
            raise ValueError(f"Embedding type {embedding_type} not supported")

    def _head_from_type(
        self,
        head_type: HeadType,
        first_party_embedding_dim: int,
        external_embedding_dim: int,
        output_dim: int,
    ) -> torch.nn.Module:
        """
        Returns a head of the given type.
        Args:
          head_type: The type of head to use.
            Currently only linear and mlp are supported.
          first_party_data_dim: The dimension of the first-party data
          external_data_dim: The dimension of the external data
          output_dim: The dimension of the output
        """
        if head_type is HeadType.LINEAR:
            return torch.nn.Linear(
                first_party_embedding_dim + external_embedding_dim, output_dim
            )
        elif head_type is HeadType.MLP:
            hidden_size = MLP_WIDTH_MULTIPLIER * (
                first_party_embedding_dim + external_embedding_dim
            )
            return torch.nn.Sequential(
                torch.nn.Linear(
                    first_party_embedding_dim + external_embedding_dim,
                    hidden_size,
                ),
                torch.nn.ReLU(),
                torch.nn.Linear(hidden_size, output_dim),
            )
        else:
            raise ValueError(f"Head type {head_type} not supported")

    def forward(
        self, x: Union[torch.Tensor, VerticallyAugmentedTensor]
    ) -> torch.Tensor:
        """
        Overrides the forward method of the base class, allowing for
        different forward passes depending on whether external data
        is passed to the model.
        """
        if isinstance(x, torch.Tensor):
            return self.module(x)
        elif self.head_module is None:
            return self.module(x.get_first_party_data())

        first_party_data: torch.Tensor = x.get_first_party_data()
        external_data: ExternalDataTensor = x.get_external_data()

        # compute first-party data embeddings
        embed_first_party = self.first_party_embedding_fn(first_party_data)
        assert (
            embed_first_party.shape[1] == self.first_party_embedding_dim
        ), "First-party embedding dimension mismatch"

        embed_external = None

        # if necessary, compute external data embeddings
        if external_data.is_raw():
            # if have not been configured to embed external data, just return
            # model processed on first-party data
            if self.external_embedding_module is None:
                return self.module(first_party_data)

            assert external_data.shape[1] == self.external_data_dim, (
                "External data dimension mismatch. Expected "
                + f"{self.external_data_dim} but got {external_data.shape[1]}"
            )

            embed_external = self.external_embedding_module(
                external_data.get_data()
            )
        elif external_data.is_embedding():
            embed_external = external_data.get_data()
        else:
            raise ValueError("External data must be either raw or embedding.")

        assert embed_external.shape[1] == self.external_embedding_dim, (
            "External embedding dimension mismatch. Expected "
            + f"{self.external_embedding_dim} but "
            + f"got {embed_external.shape[1]}"
        )

        # concatenate the external embeddings with the first-party embeddings
        concat_embeds = torch.cat([embed_first_party, embed_external], dim=1)
        return self.head_module(concat_embeds)
