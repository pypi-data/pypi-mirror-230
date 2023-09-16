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


from typing import Callable

import torch


def get_embed_dim(
    embed_fn: Callable[[torch.Tensor], torch.Tensor],
    input_dim: int,
) -> int:
    random_input = torch.randn(1, input_dim)
    embed_test = embed_fn(random_input)
    assert embed_test.dim() == 2, "Embedding function must return a 2D tensor"

    return embed_test.shape[1]


def get_output_dim(
    model: torch.nn.Module,
    input_dim: int,
) -> int:
    random_input = torch.randn(1, input_dim)
    output_test = model(random_input)
    assert output_test.dim() == 2, "Model output must be a 2D tensor"

    return output_test.shape[1]
