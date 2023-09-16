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
from torch import nn


class EmbeddingGetter(nn.Module):
    """
    Module wrapper that returns up to the penultimate layer of a model, to
    represent the embedding of the input.

    Inspired from torchvision's IntermediateLayerGetter:
    (https://github.com/pytorch/vision/blob/main/torchvision/models/_utils.py).

    It has a strong assumption that the modules have been registered
    into the model in the same order as they are used.
    This means that one should **not** reuse the same nn.Module
    twice in the forward if you want this to work.

    Additionally, it is only able to query submodules that are directly
    assigned to the model. So if `model` is passed, `model.feature1` can
    be returned, but not `model.feature1.layer2`.
    """

    def __init__(self, model: nn.Module):
        super().__init__()
        self.model = model

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = x
        children = list(self.model.named_children())

        try:
            for i in range(len(children) - 1):
                out = children[i][1](out)
        except RuntimeError:
            raise ValueError(
                "The modules that have been registered with your model "
                + "are not registered in the order that they are called "
                + "in the forward pass. Please register your modules in "
                + "the order that they are called in the forward pass, or"
                + "specify an embedding function manually."
            )

        return out
