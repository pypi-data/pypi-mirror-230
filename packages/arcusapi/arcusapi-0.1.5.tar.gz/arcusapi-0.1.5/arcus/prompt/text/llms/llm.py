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


from typing import List

from arcus.prompt.text.config import Config


class LLMOutput:
    def __init__(self, generation: str, context_summary: str):
        self.generation = generation
        self.context_summary = context_summary

    def get_generation(self) -> str:
        return self.generation

    def get_context_summary(self) -> str:
        return self.context_summary


class LLM:
    def __init__(self, model_id: str, config: Config, **kwargs):
        VALID_MODEL_IDS = self._get_valid_model_ids()
        assert model_id in VALID_MODEL_IDS, (
            "Invalid model_id "
            + f"{model_id}. Valid model_ids are: {VALID_MODEL_IDS}."
        )

        self.model_id = model_id
        self.config = config

    def get_model_id(self) -> str:
        return self.model_id

    def get_config(self) -> Config:
        return self.config

    def _get_valid_model_ids(self) -> List[str]:
        from arcus.prompt.text.llms.openai import OPENAI_MODEL_IDS

        return OPENAI_MODEL_IDS
