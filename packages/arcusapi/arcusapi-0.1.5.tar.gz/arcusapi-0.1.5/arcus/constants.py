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
import os

BEARER_PREFIX = "Bearer "
ARCUS_ENV_VAR = "ARCUS_ENVIRONMENT"
ARCUS_MODULE_NAME = "arcus"


class Environment(enum.Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    PROD = "PROD"


class API_URL(enum.Enum):
    LOCAL = "http://localhost:8080"
    DEV = "https://api.dev.arcus.co"
    PROD = "https://api.arcus.co"


class WEB_URL(enum.Enum):
    LOCAL = "http://localhost:9000"
    DEV = "https://dev.arcus.co"
    PROD = "https://app.arcus.co"


DEFAULT_ENV = Environment.PROD.value

arcus_env = os.getenv(ARCUS_ENV_VAR, DEFAULT_ENV).upper()

if arcus_env == Environment.LOCAL.value:
    ARCUS_API_URL = API_URL.LOCAL.value
    ARCUS_WEB_URL = WEB_URL.LOCAL.value
elif arcus_env == Environment.DEV.value:
    ARCUS_API_URL = API_URL.DEV.value
    ARCUS_WEB_URL = WEB_URL.DEV.value
else:
    ARCUS_API_URL = API_URL.PROD.value
    ARCUS_WEB_URL = WEB_URL.PROD.value
