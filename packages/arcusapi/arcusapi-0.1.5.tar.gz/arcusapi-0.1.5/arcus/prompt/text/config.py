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


from typing import Optional

from arcus.config import BaseConfig


class Config(BaseConfig):
    """
    Configuration for using Arcus Prompt (Text).
    """

    def __init__(
        self, api_key: str, project_id: str, llm_api_key: Optional[str] = None
    ):
        super().__init__(api_key, project_id)
        self.llm_api_key = llm_api_key

    def get_llm_api_key(self) -> Optional[str]:
        return self.llm_api_key

    def set_llm_api_key(self, api_key: str):
        self.llm_api_key = api_key
