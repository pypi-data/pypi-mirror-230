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

from retry import retry
from vhcs.plan import actions
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from ._az_facade import network_management_client as client, adjust_tags
import logging

log = logging.getLogger(__name__)


def deploy(data: dict, state: dict) -> dict:
    rg_name = data["resourceGroup"]
    vnet_name = data["vNetName"]
    name = data["name"]
    parameters = adjust_tags(data["parameters"])

    return _create(rg_name, vnet_name, name, parameters)


@retry(exceptions=ResourceExistsError, tries=10, delay=10, backoff=2, jitter=(0, 10), logger=log)
def _create(rg_name, vnet_name, name, parameters):
    return client().subnets.begin_create_or_update(rg_name, vnet_name, name, parameters).result()


def refresh(data: dict, state: dict) -> dict:
    rg_name = data["resourceGroup"]
    vnet_name = data["vNetName"]
    name = data["name"]
    try:
        return client().subnets.get(rg_name, vnet_name, name)
    except ResourceNotFoundError:
        pass


def decide(data: dict, state: dict):
    return actions.skip


def destroy(data: dict, state: dict, force: bool) -> dict:
    rg_name = data["resourceGroup"]
    vnet_name = data["vNetName"]
    name = data["name"]
    return client().subnets.begin_delete(rg_name, vnet_name, name).wait()


def eta(action: str, data: dict, state: dict):
    return "1m"
