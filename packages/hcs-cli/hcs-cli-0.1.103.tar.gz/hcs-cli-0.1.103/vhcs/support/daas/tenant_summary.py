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
from ulid import ULID
import vhcs.service.admin as admin
from vhcs.plan import context
import logging

log = logging.getLogger(__name__)


def process(data: dict, state: dict) -> dict:
    users = data["users"]
    entitlementId = data["entitlementId"]
    domainName = data["domainName"]
    stackUrl = data["stackUrl"]

    launch_items = []

    for u in users:
        horizonId = str(ULID())
        login_hint = u["userPrincipalName"]
        launch_items.append(
            {
                "userPrincipalName": u["userPrincipalName"],
                "password": u["password"],
                "launchUrl": f"{stackUrl}/appblast/webclient/?horizonId={horizonId}&entitlementId={entitlementId}&domainName={domainName}&action=start-session&login_hint={login_hint}#/desktop",
            }
        )

    uag = admin.helper.get_uags_by_edge(data["edgeId"], data["orgId"])[0]

    fqdn = uag["fqdn"]
    ip = uag["loadBalancer"]["ipAddress"]
    ret = {"uag": {"fqdn": fqdn, "ip": ip}, "logins": launch_items}

    file_name = f'{context.get("deploymentId")}-secret.yml'
    with open(file_name, "w") as file:
        yaml.dump(ret, file, sort_keys=False)

    log.info(f"Manual operation needed: update DNS {fqdn} -> {ip}.")
    log.info("Login secrets: %s", file_name)
    return ret


def destroy(data: dict, state: dict, force: bool) -> dict:
    return


def eta(action: str, data: dict, state: dict):
    return "1m"
