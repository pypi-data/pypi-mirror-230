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

from vhcs.plan import actions, context
from azure.core.exceptions import ResourceNotFoundError
from ._az_facade import network_management_client as client, adjust_tags


def deploy(data: dict, state: dict) -> dict:
    rg_name = data["resourceGroup"]
    name = data["name"]
    parameters = adjust_tags(data["parameters"])

    return client().nat_gateways.begin_create_or_update(rg_name, name, parameters).result()


def refresh(data: dict, state: dict) -> dict:
    return state


def decide(data: dict, state: dict):
    return actions.skip


def destroy(data: dict, state: dict, force: bool) -> dict:
    rg_name = data["resourceGroup"]
    name = data["name"]
    client().nat_gateways.begin_delete(rg_name, name).wait()


def eta(action: str, data: dict, state: dict):
    return "1m"
