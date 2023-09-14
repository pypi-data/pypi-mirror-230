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
import random
from . import _az_facade as az


def deploy(data: dict, state: dict) -> dict:
    group = data["group"]
    email = data["email"]
    domain_name = data["domainName"]

    pname = _convert_email_to_principle(email, domain_name)
    display_name = pname
    password = _generate_password()
    principal_name = pname
    ret = az.aad.user.create(display_name, password, principal_name)
    az.aad.group.member.add(group, ret["id"])
    ret["password"] = password
    return ret


def _convert_email_to_principle(email: str, domain_name: str) -> str:
    name = email.replace("@", "_")
    return name + "@" + domain_name


def _generate_password() -> str:
    ret = random.choices("ABCDEFGHJKMNPQRSTUVWXY")
    ret += random.choices("abcdefghjkmnpqrstuvwxy23456789", k=10)
    ret += random.choices("!@$%&*")
    return "".join(ret)


def refresh(data: dict, state: dict) -> dict:
    if state:
        id = state["id"]
        ret = az.aad.user.get(id)
        if ret:
            ret["password"] = state.get("password")
            return ret
    email = data["email"]
    domain_name = data["domainName"]
    pname = _convert_email_to_principle(email, domain_name)
    return az.aad.user.get(pname)


def decide(data: dict, state: dict):
    if not state.get("password"):
        return actions.recreate
    return actions.skip


def destroy(data: dict, state: dict, force: bool) -> dict:
    id = state["id"]
    ret = az.aad.user.delete(id)
    return ret


def eta(action: str, data: dict, state: dict):
    return "1m"
