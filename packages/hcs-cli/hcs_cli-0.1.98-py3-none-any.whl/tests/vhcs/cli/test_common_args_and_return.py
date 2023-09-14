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


class Test(CliTest):
    def test001_base_obj(self):
        expected = {"id": "i1", "opt": "o1"}
        self.verify("hcs cli-test echo-obj --opt o1 i1", expected)

    def test002_base_list(self):
        expected = [{"id": "i1", "opt": "o1"}, {"id": "i2", "opt": "o1"}]
        self.verify("hcs cli-test echo-obj-list --opt o1 i1 i2", expected)

    def test003_base_none(self):
        expected = ""
        self.verify("hcs cli-test echo-none", expected)

    def test004_base_str(self):
        expected = "hello"
        self.verify("hcs cli-test echo-str hello", expected)

    def test005_base_str_list(self):
        expected = ["hello1", "hello2"]
        self.verify("hcs cli-test echo-str-list hello1 hello2", expected)

    def test006_base_str_empty(self):
        expected = ""
        self.verify("hcs cli-test echo-str ''", expected)

    def test007_base_int(self):
        expected = 123
        self.verify("hcs cli-test echo-int 123", expected)

    def test008_base_int_list(self):
        expected = [123, 456]
        self.verify("hcs cli-test echo-int-list 123 456", expected)

    def test009_base_bool(self):
        expected = True
        self.verify("hcs cli-test echo-bool True", expected)

    def test010_base_bool_list(self):
        expected = [True, False]
        self.verify("hcs cli-test echo-bool-list true false", expected)

    def test011_base_bool(self):
        expected = 1.1
        self.verify("hcs cli-test echo-float 1.1", expected)

    def test012_base_bool_list(self):
        expected = [1.2, 1.3]
        self.verify("hcs cli-test echo-float-list 1.2 1.3", expected)

    def test100_id_only_obj(self):
        expected = '"i1"'
        self.verify("hcs --id-only cli-test echo-obj --opt o1 i1", expected)

    def test101_id_only_list(self):
        expected = ["i1", "i2"]
        self.verify("hcs --id-only cli-test echo-obj-list --opt o1 i1 i2", expected)

    def test102_id_only_short(self):
        expected = '"i1"'
        self.verify("hcs -i cli-test echo-obj --opt o1 i1", expected)

    def test110_output_json_obj(self):
        expected = {"id": "i1", "opt": "o1"}
        self.verify("hcs -o json cli-test echo-obj --opt o1 i1", expected)

    def test111_output_json_list(self):
        expected = [{"id": "i1", "opt": "o1"}, {"id": "i2", "opt": "o1"}]
        self.verify("hcs -o json cli-test echo-obj-list --opt o1 i1 i2", expected)

    def test112_output_yaml_obj(self):
        expected = """id: i1
opt: o1
"""
        self.verify("hcs -o yaml cli-test echo-obj --opt o1 i1", expected)

    def test113_output_yaml_list(self):
        expected = """- id: i1
  opt: o1
- id: i2
  opt: o1
"""
        self.verify("hcs -o yaml cli-test echo-obj-list --opt o1 i1 i2", expected)

    def test114_output_text_obj(self):
        expected = "i1"
        self.verify("hcs --id-only -o text cli-test echo-obj --opt o1 i1", expected)

    def test115_output_text_list(self):
        expected = "i1\ni2\n"
        self.verify("hcs --id-only -o text cli-test echo-obj-list --opt o1 i1 i2", expected)

    def test116_output_long(self):
        expected = """id: i1
opt: o1
"""
        self.verify("hcs --output yaml cli-test echo-obj --opt o1 i1", expected)

    def test117_output_short(self):
        expected = """id: i1
opt: o1
"""
        self.verify("hcs -oyaml cli-test echo-obj --opt o1 i1", expected)


if __name__ == "__main__":
    unittest.main()
