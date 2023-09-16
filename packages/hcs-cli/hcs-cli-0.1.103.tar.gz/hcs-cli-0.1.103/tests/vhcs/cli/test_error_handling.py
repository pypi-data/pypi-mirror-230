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


class TestErrorHandling(CliTest):
    def test001_error_simple(self):
        def verify_stderr(text):
            self.assertEqual(text, "r1")

        self.verify(
            "hcs cli-test echo-error --reason r1 --code 123 --tuple", "", 123, False, verify_stderr=verify_stderr
        )

    def test002_error_ctxp(self):
        def verify_stderr(text):
            self.assertTrue(text.find("r1") >= 0, "Root cause message must be printed")

        self.verify(
            "hcs cli-test echo-error --reason r1 --code 123 --ctxp-error", "", 123, False, verify_stderr=verify_stderr
        )

    def test010_exception_ctxp(self):
        def verify_stderr(text: str):
            self.assertTrue(text.find("pseudo-error") >= 0, "Wrapped error message must be printed")
            self.assertTrue(text.find("r1") >= 0, "Root cause message must be printed")
            self.assertTrue(text.find("KeyError") >= 0, "Root cause type must be printed")
            self.assertTrue(text.find("Traceback") < 0, "For ctxp exception, stack trace must not be printed.")

        self.verify(
            "hcs cli-test echo-exception --reason r1 --type=CtxpException", "", 1, False, verify_stderr=verify_stderr
        )

    def test011_exception_critical(self):
        def verify_stderr(text):
            self.assertTrue(text.find("pseudo-error") >= 0, "Wrapped error message must be printed")
            self.assertTrue(text.find("r1") >= 0, "Root cause message must be printed")
            self.assertTrue(text.find("KeyError") >= 0, "Root cause type must be printed")
            self.assertTrue(text.find("Traceback") >= 0, "For critical exception, stack trace must be printed.")

        self.verify(
            "hcs cli-test echo-exception --reason r1 --type=TypeError", "", 1, False, verify_stderr=verify_stderr
        )

    def test012_exception_http_status(self):
        def verify_stderr(text):
            self.assertTrue(text.find("400") >= 0, "Status code must be printed")
            self.assertTrue(text.find("r1") >= 0, "Response text must be printed")
            self.assertTrue(text.find("http://ut") >= 0, "URL must be printed")

        self.verify(
            "hcs cli-test echo-exception --reason r1 --type=httpx.HTTPStatusError",
            "",
            1,
            False,
            verify_stderr=verify_stderr,
        )

    def test013_exception_default(self):
        def verify_stderr(text):
            self.assertTrue(text.find("pseudo-error") >= 0, "Wrapped error message must be printed")
            self.assertTrue(text.find("r1") >= 0, "Root cause message must be printed")
            self.assertTrue(text.find("KeyError") >= 0, "Root cause type must be printed")
            self.assertTrue(text.find("Traceback") >= 0, "For critical exception, stack trace must be printed.")

        self.verify(
            "hcs cli-test echo-exception --reason r1 --type=Exception", "", 1, False, verify_stderr=verify_stderr
        )


if __name__ == "__main__":
    unittest.main()
