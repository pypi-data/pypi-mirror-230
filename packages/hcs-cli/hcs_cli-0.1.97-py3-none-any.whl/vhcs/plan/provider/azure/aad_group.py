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
from . import _az_facade as az


def deploy(data: dict, state: dict) -> dict:
    display_name = data["displayName"]
    mail_nickname = data["mailNickname"]
    description = data.get("description")
    parent_group = data.get("parentGroup")
    ret = az.aad.group.create(display_name, mail_nickname, description)
    if parent_group:
        az.aad.group.member.add(parent_group, ret["id"])
    return ret


def refresh(data: dict, state: dict) -> dict:
    display_name = data["displayName"]
    return az.aad.group.get(display_name)


def decide(data: dict, state: dict):
    return actions.skip


def destroy(data: dict, state: dict, force: bool) -> dict:
    if state:
        id = state["id"]
        return az.aad.group.delete(id)
    display_name = data["displayName"]
    return az.aad.group.delete(display_name)


def eta(action: str, data: dict, state: dict):
    return "1m"
