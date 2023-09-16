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


import logging
import warnings
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from arcus.config import MODE, BaseConfig
from arcus.constants import ARCUS_API_URL, ARCUS_MODULE_NAME, BEARER_PREFIX

logger = logging.getLogger(ARCUS_MODULE_NAME)

logger = logging.getLogger(__name__)

BACKOFF_TIME = 0.5
DISALLOWED_STATUS_CODES = [
    status for status in requests.status_codes._codes if status >= 400
]
RETRIABLE_METHODS = frozenset(
    ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
)


class ArcusResponse:
    """
    Wrapper around the response from an Arcus API call. Encodes whether status
    code was okay and the data returned.
    """

    data: Optional[dict]
    status_ok: bool

    def __init__(self, status_ok: bool, data: Optional[dict] = None):
        self.data = data
        self.status_ok = status_ok


class APIClient:
    """
    Base class for API clients. Provides a common interface for making
    requests to the Arcus API.
    """

    def __init__(self, config: BaseConfig, num_retries: int = 5):
        self.config = config
        self.num_retries = num_retries
        self.session = requests.Session()
        retry = Retry(
            total=self.num_retries,
            backoff_factor=BACKOFF_TIME,
            raise_on_redirect=False,
            raise_on_status=False,
            status_forcelist=DISALLOWED_STATUS_CODES,
            allowed_methods=RETRIABLE_METHODS,
        )
        self.session.mount(
            "https://",
            HTTPAdapter(max_retries=retry),
        )
        self.session.mount(
            "http://",
            HTTPAdapter(max_retries=retry),
        )

    def _create_auth_headers(self) -> Dict:
        return {
            "Authorization": BEARER_PREFIX + self.config.get_api_key(),
        }

    def _append_auth_header(self, headers: Optional[Dict] = None) -> Dict:
        """
        Given a set of headers, construct a new set of headers with the
        authentication headers added.
        """
        if headers is None:
            return self._create_auth_headers()

        headers.update(self._create_auth_headers())
        return headers

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> ArcusResponse:
        """
        Wrapper around requests.request that adds authentication headers and
        raises warnings in the case of errors.
        Args:
            method: HTTP method to use.
            path: Path to append to the base URL.
            params: Query parameters to pass to the request.
            json: JSON body to pass to the request.
            headers: Headers to pass to the request.
        Returns:
            ArcusResponse object containing the response data and whether the
            status code was okay.
        """

        headers = self._append_auth_header(headers)

        response = self.session.request(
            method,
            f"{ARCUS_API_URL}/{path}",
            params=params,
            json=json,
            headers=headers,
        )

        if self.config.mode == MODE.DEBUG:
            logger.debug(
                f"Request to {path} with parameters {params} took: "
                + f"{response.elapsed.total_seconds()}s."
            )

        if not response.ok:
            warnings.warn(
                f"Request {method} {ARCUS_API_URL}/{path} failed with"
                + f"status code {response.status_code} and message"
                + f"{response.text}."
            )

        # API client passes along whether status is okay to downstream
        # libraries to process as needed.
        return ArcusResponse(
            data=response.json() if response.ok else response.text,
            status_ok=response.ok,
        )
