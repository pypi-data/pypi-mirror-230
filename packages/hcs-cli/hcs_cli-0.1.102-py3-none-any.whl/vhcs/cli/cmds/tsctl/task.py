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
from vhcs.service import tsctl
import vhcs.sglib.cli_options as cli


@click.command()
def list_namespaces(**kwargs):
    """List namespaces"""
    return tsctl.list_namespaces()


@click.group(name="task")
def task_cmd_group():
    pass


@task_cmd_group.command()
@click.option("--namespace", "-n", type=str, required=True)
@cli.search
def list(namespace: str, **kwargs):
    """List tasks"""
    return tsctl.task.list(namespace, **kwargs)


@task_cmd_group.command()
@click.option("--namespace", "-n", type=str, required=True)
@click.option("--id", "-i", type=str, required=True)
def get(namespace: str, id: str, **kwargs):
    """Get task by ID"""
    return tsctl.task.get(namespace, id, **kwargs)


@task_cmd_group.command()
@click.option("--namespace", "-n", type=str, required=True)
@click.option("--group", "-g", type=str, required=True)
@click.option("--key", "-k", type=str, required=True)
def delete(namespace: str, group: str, key: str, **kwargs):
    """Delete task by ID"""
    return tsctl.task.delete(namespace, group, key, **kwargs)


@task_cmd_group.command()
@click.option("--namespace", "-n", type=str, required=True)
@cli.search
def logs(namespace: str, **kwargs):
    """List logs by task"""
    return tsctl.task.logs(namespace, **kwargs)
