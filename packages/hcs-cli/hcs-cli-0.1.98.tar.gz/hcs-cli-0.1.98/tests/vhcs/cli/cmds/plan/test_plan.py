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

import yaml
import os
import re
import unittest
from typing import Any, Callable
from test_utils import CliTest
from vhcs.ctxp.data_util import deep_get_attr

_blueprints = [
    # basic
    """
deploymentId: d10
resource:
  r1:
    kind: dev/dummy
""",
    # basic dep
    """
deploymentId: d11
var:
    guestName: Alice
resource:
  r1:
    kind: dev/dummy
    data:
        text: ${var.guestName}
        delay: 1s
  r2:
    kind: dev/dummy
    data:
        text: ${r1.outputText}
""",
    # basic_dep_double
    """
deploymentId: d12
resource:
  r1a:
    kind: dev/dummy
    data:
        text: a
        delay: 2s
  r1b:
    kind: dev/dummy
    data:
        text: b
        delay: 2s
  r2:
    kind: dev/dummy
    data:
        text: ${r1a.outputText}, ${r1b.outputText}
""",
    # basic_parallel
    """
deploymentId: d20
resource:
  r1:
    kind: dev/dummy
    data:
        delay: 2s
  r2:
    kind: dev/dummy
""",
    # basic_parallel2
    """
deploymentId: d21
resource:
  r1:
    kind: dev/dummy
    data:
      text: a
      delay: 4s
  r2a:
    kind: dev/dummy
    data:
      text: a
      delay: 1s
  r2b:
    kind: dev/dummy
    data:
      text: ${r2a.outputText}
      delay: 1s
  r2c:
    kind: dev/dummy
    data:
      text: ${r2b.outputText}
      delay: 1s
""",
    # basic_error_sequential
    """
deploymentId: d30
resource:
  r1:
    kind: dev/dummy
    data:
        error: A simulated error
  r2:
    kind: dev/dummy
    data:
        text: ${r1.outputText}
""",
    # basic_error_parallel
    """
deploymentId: d31
resource:
  r1:
    kind: dev/dummy
    data:
        error: A simulated error
        delay: 1s
  r2:
    kind: dev/dummy
""",
    # basic_multipath
    """
deploymentId: d40
resource:
  level1_head1:
    kind: dev/dummy
  level1_head2:
    kind: dev/dummy
  level1_head3:
    kind: dev/dummy
  level2_h1a:
    kind: dev/dummy
    after:
    - level1_head1
  level2_h1b:
    kind: dev/dummy
    after: 
    - level1_head1
  level2_h2:
    kind: dev/dummy
    after:
    - level1_head2
  level3_a:
    kind: dev/dummy
    after:
    - level2_h1a
  level3_b:
    kind: dev/dummy
    after:
    - level2_h1b
    - level2_h2
  level4:
    kind: dev/dummy
    after:
    - level1_head3
    - level3_b
""",
    # basic_statement_after
    """
deploymentId: d50
resource:
  r1:
    kind: dev/dummy
    data:
        delay: 1s
  r2:
    kind: dev/dummy
    after:
    - r1
""",
    # basic_statement_for
    """
deploymentId: d60
var:
  userEmails:
    - a@t.com
    - b@t.com
resource:
  r1:
    kind: dev/dummy
    for: text in var.userEmails
""",
    # list_map_expression
    """
deploymentId: d70
var:
  userEmails:
    - a@t.com
    - b@t.com
resource:
  r1:
    kind: dev/dummy
    for: text in var.userEmails
  r2:
    kind: dev/dummy
    data:
      agg: "${[for r in r1: r.outputText]}"
""",
    # basic_condition
    """
deploymentId: d80
var:
  guest1: Alice
  guest2:
resource:
  r1:
    kind: dev/dummy
    conditions:
      has_guest1: ${var.guest1}
    data:
      text: hello
  r2:
    kind: dev/dummy
    conditions:
      has_guest2: ${var.guest2}
    data:
      text: hello
  r11:
    kind: dev/dummy
    conditions:
      has_r1: ${r1.outputText}
  r21:
    kind: dev/dummy
    conditions:
      has_r2: ${r2.outputText}
""",
    # basic_runtime
    """
deploymentId: d90
runtime:
  rt1:
    impl: vhcs.plan.provider.dev.fibonacci
    data:
      n: 10
""",
    # use_env
    """
deploymentId: d100
resource:
  r1:
    kind: dev/dummy
    data:
      text: hello, ${env._MY_GUEST_NAME}
""",
    # use_env_more
    """
deploymentId: d101
var:
  guestName: ${env._MY_GUEST_NAME} Jr.
defaults:
  actualName: ${var.guestName}'s cat ${env._MY_PET_NAME} 
resource:
  r1:
    kind: dev/dummy
    data:
      text: hello, ${defaults.actualName}
""",
    # env_not_found
    """
deploymentId: d102
resource:
  r1:
    kind: dev/dummy
    data:
      text: hello, ${env._MY_NOT_FOUND_ENV}
""",
]

_bp_map = {}


def _create_bp_map():
    pattern = re.compile(r"^deploymentId\:\s*(\w+)$")
    for bp in _blueprints:
        dpid = None
        for line in bp.splitlines():
            m = pattern.match(line)
            if m:
                dpid = m.group(1)
                break
        if not dpid:
            raise Exception("Invalid blueprint: deployment id not found: \n" + bp)
        _bp_map[dpid] = bp


_create_bp_map()


def _get_blueprint(deployment_id: str):
    return _bp_map[deployment_id]


class TestPlan(CliTest):
    @classmethod
    def setUpClass(cls):
        _cleanup_states()

    @classmethod
    def tearDownClass(cls):
        _cleanup_states()

    def test10_basic(self):
        dpid = "d10"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_destroy(bp)

    def test11_basic_dep(self):
        dpid = "d11"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid,
            "create",
            "r2 must be deployed after r1",
            precise_order=["start/r1", "success/r1", "start/r2", "success/r2"],
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid,
            "delete",
            "r2 must be destroyed before r1",
            precise_order=["start/r2", "success/r2", "start/r1", "success/r1"],
        )

    def test12_basic_dep_double(self):
        dpid = "d12"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid, "create", "r2 must be deployed after r1a", partial_order=["success/r1a", "start/r2"]
        )
        self.verify_execution_log(
            dpid, "create", "r2 must be deployed after r1b", partial_order=["success/r1b", "start/r2"]
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid, "delete", "r2 must be destroyed before r1a", partial_order=["success/r2", "start/r1a"]
        )
        self.verify_execution_log(
            dpid, "delete", "r2 must be destroyed before r1a", partial_order=["success/r2", "start/r1b"]
        )

    def test20_basic_parallel(self):
        dpid = "d20"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid, "create", "success of r2 must before success of r1", partial_order=["success/r2", "success/r1"]
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid, "delete", "both r1 and r2 must be destroyed", any_order=["success/r2", "success/r1"]
        )

    def test21_basic_parallel2(self):
        dpid = "d21"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid,
            "create",
            "r2b and r2c runs in parallel as r1",
            partial_order=["start/r1", "start/r2b", "success/r2b", "start/r2c", "success/r2c", "success/r1"],
        )
        self.verify_destroy(bp)

    def test30_basic_error_sequential(self):
        dpid = "d30"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp, expected_return_code=1)
        self.verify_execution_log(
            dpid, "create", "r2 must not be deployed, due to failure in r1", precise_order=["start/r1", "error/r1"]
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid,
            "delete",
            "r2 must not be destroyed, since it's not deployed",
            precise_order=["skip/r2", "start/r1", "success/r1"],
        )

    def test31_basic_error_parallel(self):
        dpid = "d31"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp, expected_return_code=1)
        self.verify_execution_log(
            dpid, "create", "success of r2 must before error of r1", partial_order=["success/r2", "error/r1"]
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid, "delete", "both r1 and r2 must be cleaned up", any_order=["success/r2", "success/r1"]
        )

    def test40_basic_multipath(self):
        dpid = "d40"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_destroy(bp)

    def test50_basic_statement_after(self):
        dpid = "d50"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid,
            "create",
            "r2 must be deployed after r1",
            precise_order=["start/r1", "success/r1", "start/r2", "success/r2"],
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid,
            "delete",
            "r2 must be destroyed before r1",
            precise_order=["start/r2", "success/r2", "start/r1", "success/r1"],
        )

    def test60_basic_statement_for(self):
        dpid = "d60"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid,
            "create",
            "r1 must be deployed twice with an additional one for the group",
            partial_order=["success/r1#0", "success/r1#1", "success/r1"],
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid,
            "delete",
            "r1 must be destroyed twice with an additional one for the group",
            any_order=["success/r1#0", "success/r1#1", "success/r1"],
        )

    def test70_list_map_expression(self):
        dpid = "d70"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid,
            "create",
            "three r1 instances must be created before r2 start",
            partial_order=["success/r1#0", "success/r1#1", "success/r1", "start/r2", "success/r2"],
        )
        self.verify_output(dpid, "output.r2.agg", ["a@t.com", "b@t.com"])
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid,
            "delete",
            "r1 group must be deleted after r2",
            partial_order=["start/r2", "success/r2", "start/r1", "start/r1#0"],
        )

    def test80_basic_condition(self):
        dpid = "d80"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(
            dpid,
            "create",
            "r1 and r11 are deployed. r2 and r21 are not.",
            partial_order=["success/r1", "success/r11"],
            any_order=["skip/r2", "skip/r21"],
        )
        self.verify_destroy(bp)
        self.verify_execution_log(
            dpid,
            "delete",
            "r1 and r11 are destroyed. r2 and r22 are not.",
            partial_order=["success/r11", "success/r1"],
            any_order=["skip/r2", "skip/r21"],
        )

    def test90_basic_runtime(self):
        dpid = "d90"
        bp = _get_blueprint(dpid)
        self.verify_deploy(bp)
        self.verify_execution_log(dpid, "create", "rt1 must success", precise_order=["start/rt1", "success/rt1"])
        self.verify_resource_output(dpid, "rt1", {"fibonacci": 34}, "The runtime must do the calculation.")
        self.verify_destroy(bp)
        self.verify_execution_log(dpid, "delete", "rt1 must success", precise_order=["start/rt1", "success/rt1"])

    def test100_use_env(self):
        dpid = "d100"
        bp = _get_blueprint(dpid)
        os.environ["_MY_GUEST_NAME"] = "Bob"
        self.verify_deploy(bp)
        expected_output = {"text": "hello, Bob", "outputText": "hello, Bob", "n": 0}
        self.verify_resource_output(dpid, "r1", expected_output, msg="The env value 'Bob' must appear.")
        self.verify_destroy(bp)

    def test101_use_env_more(self):
        dpid = "d101"
        bp = _get_blueprint(dpid)
        os.environ["_MY_GUEST_NAME"] = "Bob"
        os.environ["_MY_PET_NAME"] = "Telangpu"
        self.verify_deploy(bp)
        expected_output = {
            "text": "hello, Bob Jr.'s cat Telangpu",
            "outputText": "hello, Bob Jr.'s cat Telangpu",
            "n": 0,
        }
        self.verify_resource_output(dpid, "r1", expected_output, "The environment vars must be used.")
        self.verify_destroy(bp)

    def test102_env_not_found(self):
        dpid = "d102"
        bp = _get_blueprint(dpid)

        def verify_stderr(text: str):
            self.assertTrue(text.find("_MY_NOT_FOUND_ENV") > 0, "Error message must contain the missing env name")

        # os.environ['_MY_NOT_FOUND_ENV'] = None
        self.verify(
            "hcs plan apply -f -",
            expected_stdout="",
            expected_return_code=1,
            expect_stderr_empty=False,
            verify_stderr=verify_stderr,
            stdin_payload=bp,
        )

    def verify_deploy(self, stdin_payload: str, expected_return_code: int = 0):
        self.verify(
            "hcs plan apply -f -",
            expected_stdout="",
            expected_return_code=expected_return_code,
            expect_stderr_empty=False,
            stdin_payload=stdin_payload,
        )

    def verify_destroy(self, stdin_payload: str, expected_return_code: int = 0):
        self.verify(
            "hcs plan destroy -f -",
            expected_stdout="",
            expected_return_code=expected_return_code,
            expect_stderr_empty=False,
            stdin_payload=stdin_payload,
        )

    def verify_output(self, deployment_id: str, res_path: str, expected_value):
        with open(f"{deployment_id}.state.yml", "rt") as file:
            state = yaml.safe_load(file)
        v = deep_get_attr(state, res_path)
        self.assertEqual(v, expected_value)

    def verify_execution_log(
        self,
        deployment_id: str,
        method: str,
        description: str,
        precise_order: list[str] = None,
        partial_order: list[str] = None,
        any_order: list[str] = None,
    ):
        with open(f"{deployment_id}.state.yml", "rt") as file:
            state = yaml.safe_load(file)
        exec_logs = state["log"][method]

        actual_execution_order = []
        for entry in exec_logs:
            actual_execution_order.append(entry["action"] + "/" + entry["name"])

        if precise_order:
            self.assertEqual(actual_execution_order, precise_order, description)
        elif partial_order:
            filtered_order = [x for x in actual_execution_order if x in partial_order]
            self.assertEqual(filtered_order, partial_order, description)
        elif any_order:
            s1 = set(actual_execution_order)
            s2 = set(any_order)
            try:
                self.assertTrue(s1 > s2, description)
            except:
                print("DUMP actual_execution_order: ", actual_execution_order)
                print("DUMP expectation (any_order): ", any_order)
                raise
        else:
            raise Exception("One of the following must be specified: precise_order, partial_order, any_order")

    def verify_resource_output(self, deployment_id: str, resource_id: str, expected_stdout: Any, msg: str):
        with open(f"{deployment_id}.state.yml", "rt") as file:
            state = yaml.safe_load(file)
        output = state["output"][resource_id]

        self.assertEqual(output, expected_stdout, msg)


def _cleanup_states():
    # names = filter(lambda name: not name.startswith('__'), dir(_blueprints))
    # pattern = r"deploymentId:\s+(\w+)"
    # for name in names:
    #     value = getattr(_blueprints, name)
    #     m = re.search(pattern, value)
    #     deployment_id = m.group(1)

    #     state_file_name = f'{deployment_id}.state.yml'
    #     if os.path.exists(state_file_name):
    #         os.unlink(state_file_name)
    for dpid in _bp_map.keys():
        state_file_name = f"{dpid}.state.yml"
        if os.path.exists(state_file_name):
            os.unlink(state_file_name)


if __name__ == "__main__":
    unittest.main()
