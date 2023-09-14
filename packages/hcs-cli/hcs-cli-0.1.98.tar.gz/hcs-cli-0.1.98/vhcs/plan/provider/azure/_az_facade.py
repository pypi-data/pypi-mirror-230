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

import subprocess
import json
import logging

log = logging.getLogger(__name__)

_subscription = None


def _az(command: str, silent: bool = False) -> dict:
    log.debug(command)
    args = command.split(" ")
    p = subprocess.run(args, capture_output=True, text=True, timeout=None, check=False)
    if p.returncode:
        if silent:
            pass
        else:
            log.error("RETURN: " + str(p.returncode))
            log.error("STDOUT: " + p.stdout)
            log.error("STDERR: " + p.stderr)
            raise subprocess.CalledProcessError(p.returncode, p.args, output=p.stdout, stderr=p.stderr)
    else:
        if p.stdout:
            try:
                return json.loads(p.stdout)
            except Exception as e:
                log.error("Fail parsing response %s", e)
                log.warning("Payload: %s", p.stdout)


def login(username: str, password: str, tenant_id: str):
    return _az(f"az login --service-principal -u {username} -p {password} --tenant {tenant_id}")


def _formalize_tags(tags: dict) -> str:
    list_tags = []
    if tags:
        for k, v in tags.items():
            list_tags.append(f"{k}={v}")
    return " ".join(list_tags)


def set_subscription(id: str):
    global _subscription
    _subscription = id
    return _az(f"az account set --subscription {id}")


def locations():
    return _az("az account list-locations")


class resource_group:
    @staticmethod
    def create(name: str, location: str, tags: dict = None):
        tags_str = _formalize_tags(tags)
        return _az(f"az group create --location {location} --name {name} --tags {tags_str}")

    @staticmethod
    def delete(name: str):
        exists = _az(f"az group exists --name {name}")
        if exists:
            _az(f"az group delete --name {name} --yes")
            return True
        return False


class _aad_group_member:
    @staticmethod
    def list(id_or_display_name: str):
        return _az(f"az ad group member list --group {id_or_display_name}")

    @staticmethod
    def add(id_or_display_name: str, member_id: str):
        return _az(f"az ad group member add --group {id_or_display_name} --member-id {member_id}")


class _aad_group:
    member = _aad_group_member

    @staticmethod
    def create(display_name: str, mail_nickname: str, description: str = None):
        cmd = f"az ad group create --display-name {display_name} --mail-nickname {mail_nickname}"
        if description:
            cmd += f" --description {description}"
        return _az(cmd)

    @staticmethod
    def get(id_or_display_name: str):
        return _az(f"az ad group show --group {id_or_display_name}", silent=True)

    @staticmethod
    def delete(id_or_display_name: str):
        return _az(f"az ad group delete --group {id_or_display_name}")

    @staticmethod
    def list():
        return _az(f"az ad group list")


class _aad_user:
    @staticmethod
    def create(display_name: str, password: str, principal_name: str):
        return _az(
            f"az ad user create --display-name {display_name} --password {password} --user-principal-name {principal_name}"
        )

    @staticmethod
    def get(id_or_principal_name: str):
        return _az(f"az ad user show --id {id_or_principal_name}", silent=True)

    @staticmethod
    def delete(id: str):
        return _az(f"az ad user delete --id {id}")


class aad:
    group = _aad_group
    user = _aad_user


class _vnet:
    @staticmethod
    def get(id: str):
        return _az(f"az network vnet show --ids {id}")

    @staticmethod
    def create(rg_name: str, name: str, address_prefix: str):
        return _az(f"az network vnet create -g {rg_name} -n {name} --address-prefix {address_prefix}")

    @staticmethod
    def delete(rg_name: str, name: str, address_prefix: str):
        return _az(f"az network vnet create -g {rg_name} -n {name} --address-prefix {address_prefix}")

    @staticmethod
    def list():
        return _az("az network vnet list")


class _nsg:
    @staticmethod
    def create(rg_name: str, name: str, location: str, tags: list[str] = None):
        tags_str = _formalize_tags(tags)
        return _az(f"az network nsg create -g {rg_name} -n {name} --location {location} --tags {tags_str}")

    @staticmethod
    def delete_by_id(id: str):
        return _az(f"az network nsg delete --ids {id}")

    @staticmethod
    def delete(rg_name: str, name: str):
        return _az(f"az network nsg delete -g {rg_name} -n {name}")


class _subnet:
    @staticmethod
    def create(rg_name: str, vnet_name: str, name: str, cidr: str, nsg_name: str):
        return _az(
            f"az network vnet subnet create -g {rg_name} --vnet-name {vnet_name} -n {name} --address-prefixes {cidr} --network-security-group {nsg_name}"
        )

    @staticmethod
    def delete_by_id(id: str):
        return _az(f"az network vnet subnet delete --ids {id}")

    @staticmethod
    def delete(rg_name: str, vnet_name: str, name: str):
        return _az(f"az network vnet subnet delete -g {rg_name} --vnet-name {vnet_name} -n {name}")

    @staticmethod
    def list(rg_name: str, vnet_name: str):
        return _az(f"az network vnet subnet list -g {rg_name} --vnet-name {vnet_name}")


class _public_ip:
    @staticmethod
    def create(rg_name: str, name: str, location: str):
        return _az(
            f"az network public-ip create -g {rg_name} -n {name} --location {location} --allocation-method Static"
        )

    @staticmethod
    def get(rg_name: str, name: str):
        return _az(f"az network public-ip show -g {rg_name} -n {name}")

    @staticmethod
    def delete(rg_name: str, name: str):
        return _az(f"az network public-ip delete -g {rg_name} -n {name}")


class network:
    vnet = _vnet
    nsg = _nsg
    subnet = _subnet
    public_ip = _public_ip


def adjust_tags(parameters) -> str:
    return parameters


from vhcs.plan import context
from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.msi import ManagedServiceIdentityClient


def network_management_client() -> NetworkManagementClient:
    credentials = AzureCliCredential()
    return NetworkManagementClient(credentials, _subscription)


def resource_management_client() -> ResourceManagementClient:
    credentials = AzureCliCredential()
    return ResourceManagementClient(credentials, _subscription)


def managed_identity_client() -> ManagedServiceIdentityClient:
    credentials = AzureCliCredential()
    return ManagedServiceIdentityClient(credentials, _subscription)
