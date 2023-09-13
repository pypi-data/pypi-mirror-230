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
from vhcs.service.org_service import details


@click.command("list")
@click.option(
    "--limit", "-l", type=int, required=False, default=20, help="Optionally, specify the number of records to return."
)
@click.option(
    "--search",
    "-s",
    type=str,
    required=False,
    help="Specify the REST-search string. E.g. 'orgId $eq 21eb79bc-f737-479f-b790-7753da55f363 AND orgName $like VMW'. Note, in bash/sh/zsh, use single quote.",
)
def list_org_details(limit: int, search: str):
    """List all org details"""
    ret = details.list(limit=limit, search=search)
    return ret
