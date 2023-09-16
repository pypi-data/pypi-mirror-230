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


import os
import unittest
from importlib import reload
from unittest.mock import patch


class TestLocal(unittest.TestCase):
    @patch.dict(os.environ, {"ARCUS_ENVIRONMENT": "loCal"})
    def test_local(self):
        from arcus import constants

        # reload the module to get the new environment variable
        constants = reload(constants)

        self.assertEqual(
            constants.ARCUS_API_URL,
            "http://localhost:8080",
        )
        self.assertEqual(
            constants.ARCUS_WEB_URL,
            "http://localhost:9000",
        )


class TestDev(unittest.TestCase):
    @patch.dict(os.environ, {"ARCUS_ENVIRONMENT": "dEv"})
    def test_dev(self):
        from arcus import constants

        # reload the module to get the new environment variable
        constants = reload(constants)

        self.assertEqual(
            constants.ARCUS_API_URL,
            "https://api.dev.arcus.co",
        )
        self.assertEqual(
            constants.ARCUS_WEB_URL,
            "https://dev.arcus.co",
        )


class TestProd(unittest.TestCase):
    @patch.dict(os.environ, {"ARCUS_ENVIRONMENT": "pRoD"})
    def test_prod(self):
        from arcus import constants

        # reload the module to get the new environment variable
        constants = reload(constants)

        self.assertEqual(
            constants.ARCUS_API_URL,
            "https://api.arcus.co",
        )
        self.assertEqual(
            constants.ARCUS_WEB_URL,
            "https://app.arcus.co",
        )


class TestDefault(unittest.TestCase):
    @patch.dict(os.environ, {"ARCUS_ENVIRONMENT": "SOME_OTHER_ENV"})
    def test_default(self):
        from arcus import constants

        # reload the module to get the new environment variable
        constants = reload(constants)

        self.assertEqual(
            constants.ARCUS_API_URL,
            "https://api.arcus.co",
        )
        self.assertEqual(
            constants.ARCUS_WEB_URL,
            "https://app.arcus.co",
        )


class TestNoEnv(unittest.TestCase):
    # This test is to make sure that the environment variable is not set
    # in the environment when the test is run. This is to make sure that
    # the default value is used.
    def setUp(self) -> None:
        super().setUp()
        self.old_env = os.environ.get("ARCUS_ENVIRONMENT")
        if self.old_env:
            del os.environ["ARCUS_ENVIRONMENT"]

    # After the test is run, set the environment variable back to what it was.
    def tearDown(self) -> None:
        super().tearDown()
        if self.old_env:
            os.environ["ARCUS_ENVIRONMENT"] = self.old_env

    def test_no_env(self):
        from arcus import constants

        # reload the module to get the new environment variable
        constants = reload(constants)

        self.assertEqual(
            constants.ARCUS_API_URL,
            "https://api.arcus.co",
        )
        self.assertEqual(
            constants.ARCUS_WEB_URL,
            "https://app.arcus.co",
        )
