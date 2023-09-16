"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from test_utils import CliTest


class TestProfile(CliTest):
    def test1(self):
        self.verify("hcs profile", CliTest.NON_EMPTY_STRING)

    def test2_happy(self):
        self.verify("hcs profile list", CliTest.NON_EMPTY_JSON)
        self.verify("hcs profile file", CliTest.NON_EMPTY_STRING)
        self.verify("hcs profile get", CliTest.NON_EMPTY_JSON)
        self.verify("hcs profile create", "", 2, False)
        self.verify("hcs profile delete _inexist_profile_ut", "")


if __name__ == "__main__":
    unittest.main()
