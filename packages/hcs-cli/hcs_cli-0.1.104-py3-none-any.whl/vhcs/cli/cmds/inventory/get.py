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

import click
from vhcs.service import inventory
import vhcs.sglib.cli_options as cli


@click.command()
@click.option("--template", "-t", type=str, required=True, help="Template id")
@click.option("--vm", "-v", type=str, required=True, help="VM id")
@cli.org_id
def get(template: str, vm: str, org: str):
    """Get template by ID"""
    ret = inventory.get(template, vm, cli.get_org_id(org))
    if ret:
        return ret
    return ret, 1
