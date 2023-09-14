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


class TestContext(CliTest):
    def test1_default_help(self):
        self.verify("hcs context", CliTest.NON_EMPTY_STRING)
        self.verify("hcs context --help", CliTest.NON_EMPTY_STRING)

    def test2_invalid_set(self):
        self.verify("hcs context set a b", "", 1, False)

    def test3_happy(self):
        self.verify("hcs context list", [])

        self.verify("hcs context set a k1=v1", "")
        self.verify("hcs context list", ["a"])

        self.verify("hcs context get a", {"k1": "v1"})
        self.verify("hcs context get a k1", "v1")
        self.verify("hcs context set a k1=v1", "")
        self.verify("hcs context set a k2=v2", "")
        self.verify("hcs context get a", {"k1": "v1", "k2": "v2"})
        self.verify("hcs context set a k1=33", "")
        self.verify("hcs context get a", {"k1": "33", "k2": "v2"})
        self.verify("hcs context get a k1", "33")
        self.verify("hcs context get a k2", "v2")
        self.verify("hcs context set a k1=", "")
        self.verify("hcs context get a", {"k1": "", "k2": "v2"})
        self.verify("hcs context delete a", "")
        self.verify("hcs context get a", "")
        self.verify("hcs context delete a", "")
        self.verify("hcs context list", [])


if __name__ == "__main__":
    unittest.main()
