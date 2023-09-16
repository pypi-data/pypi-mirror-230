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


import enum
import logging
import os
import sys

from arcus.constants import ARCUS_MODULE_NAME

ARCUS_MODE_VAR = "ARCUS_MODE"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(ARCUS_MODULE_NAME)


class MODE(enum.Enum):
    DEBUG = "DEBUG"
    PROD = "PROD"


DEFAULT_MODE = MODE.PROD.value


class BaseConfig:
    def __init__(
        self,
        api_key: str,
        project_id: str,
    ):
        """
        Configuration for a generic Arcus project.
        """

        self.api_key = api_key
        self.project_id = project_id

        mode = os.getenv(ARCUS_MODE_VAR, DEFAULT_MODE).upper()
        if mode == MODE.DEBUG.value:
            logger.setLevel(logging.DEBUG)
            self.mode = MODE.DEBUG
        else:
            self.mode = MODE.PROD

    def get_api_key(self) -> str:
        return self.api_key

    def get_project_id(self) -> str:
        return self.project_id
