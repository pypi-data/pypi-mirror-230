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

from vhcs.plan import actions
from azure.core.exceptions import ResourceNotFoundError
from ._az_facade import network_management_client as client, adjust_tags


def deploy(data: dict, state: dict) -> dict:
    name = data["name"]
    resource_group = data["resourceGroup"]
    parameters = adjust_tags(data["parameters"])

    return client().public_ip_addresses.begin_create_or_update(resource_group, name, parameters).result()


def refresh(data: dict, state: dict) -> dict:
    name = data["name"]
    resource_group = data["resourceGroup"]
    try:
        return client().public_ip_addresses.get(resource_group, name)
    except ResourceNotFoundError:
        pass


def decide(data: dict, state: dict):
    return actions.create


def destroy(data: dict, state: dict, force: bool) -> dict:
    name = data["name"]
    resource_group = data["resourceGroup"]
    client().public_ip_addresses.begin_delete(resource_group, name).wait()


def eta(action: str, data: dict, state: dict):
    return "1m"
