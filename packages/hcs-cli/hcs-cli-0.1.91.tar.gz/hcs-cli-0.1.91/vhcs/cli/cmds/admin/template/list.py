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
from vhcs.service import admin
import vhcs.sglib.cli_options as cli


@click.command()
@cli.org_id
@click.option("--limit", "-l", type=int, required=False, default=20, help="Optionally, specify cloud provider type.")
@click.option("--brokerable-only", type=bool, required=False, default=False)
@click.option("--expanded", type=bool, required=False, default=False)
@click.option(
    "--reported-search",
    type=str,
    required=False,
    help="Search expression for selection of template reported properties",
)
@click.option("--template-search", type=str, required=False, help="Search expression for selection of templates")
@click.option(
    "--sort",
    type=str,
    required=False,
    help="Ascending/Descending. Format is property,{asc|desc} and default is ascending",
)
def list(
    org: str, limit: int, brokerable_only: bool, expanded: bool, reported_search: str, template_search: str, sort: str
):
    """List templates"""
    org_id = cli.get_org_id(org)
    return admin.template.list(
        org_id=org_id,
        limit=limit,
        borkerable_only=brokerable_only,
        expanded=expanded,
        reported_search=reported_search,
        template_search=template_search,
        sort=sort,
    )
