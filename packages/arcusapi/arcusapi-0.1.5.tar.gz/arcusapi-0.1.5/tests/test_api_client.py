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


import unittest
import unittest.mock as mock
from typing import Dict, Optional
from unittest.mock import MagicMock

from arcus.api_client import APIClient
from arcus.constants import ARCUS_API_URL


class MockResponse:
    def __init__(self, data: dict, status_code: int, text: str = ""):
        self.data = data
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = text

    def json(self) -> str:
        return self.data


def mocked_requests_request(
    method: str,
    url: str,
    params: Optional[Dict] = None,
    json: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    **kwargs,
):
    if (
        method == "GET"
        and url == f"{ARCUS_API_URL}/test"
        and headers
        == {
            "Authorization": "Bearer test",
            "test": "test",
        }
    ):
        return MockResponse({"key1": "value1"}, 200)

    return MockResponse("", 404, "not found")


class TestCreateAuthHeaders(unittest.TestCase):
    def test_construct_headers(self):
        config = MagicMock()
        config.get_api_key.return_value = "test"
        config.get_project_id.return_value = "test"
        existing_headers = {"test": "test"}

        api_client = APIClient(config)

        headers = api_client._append_auth_header(existing_headers)

        self.assertEqual(
            headers,
            {
                "Authorization": "Bearer test",
                "test": "test",
            },
        )


class TestApiClient(unittest.TestCase):
    @mock.patch(
        "requests.Session.request", side_effect=mocked_requests_request
    )
    def test_create_arcus_request(self, mock_request):
        method = "GET"
        path = "test"
        config = MagicMock()
        config.get_api_key.return_value = "test"
        config.get_project_id.return_value = "test"
        params = {"test": "test"}
        json = {"test": "test"}
        headers = {"test": "test"}

        api_client = APIClient(config)

        response = api_client.request(method, path, params, json, headers)
        self.assertEqual(response.data, {"key1": "value1"})
        self.assertEqual(response.status_ok, True)

    @mock.patch(
        "requests.Session.request", side_effect=mocked_requests_request
    )
    def test_create_arcus_request_fail(self, mock_request):
        method = "GET"
        path = "test2"
        config = MagicMock()
        config.get_api_key.return_value = "test"
        config.get_project_id.return_value = "test"
        params = {"test": "test"}
        json = {"test": "test"}
        headers = {"test": "test"}

        api_client = APIClient(config)

        with self.assertWarns(UserWarning):
            response = api_client.request(method, path, params, json, headers)
            self.assertEqual(response.data, "not found")
            self.assertEqual(response.status_ok, False)


if __name__ == "__main__":
    unittest.main()
