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
from vhcs.ctxp import profile
from vhcs.plan import PlanException


def load_plan(file):
    if not file:
        file = _try_locating_plan_file()

    with file:
        payload = file.read()
    data = yaml.safe_load(payload)
    extra = {"profile": profile.current(exclude_secret=True)}
    return data, extra


def _try_locating_plan_file():
    files = os.listdir()
    candidates = []
    for name in files:
        if name.endswith(".plan.yml"):
            if candidates:
                raise PlanException(
                    "Multiple plan files exist. Use the --file parameter to specify a target plan file."
                )
            candidates.append(name)
    if not candidates:
        raise PlanException("No plan yaml file found. Use the --file parameter to specify a target plan file.")
    return open(candidates[0], "rt")
