# Copyright (c) Mengning Software. 2023. All rights reserved.
#
# Super IDE licensed under GNU Affero General Public License v3 (AGPL-3.0) .
# You can use this software according to the terms and conditions of the AGPL-3.0.
# You may obtain a copy of AGPL-3.0 at:
#
#    https://www.gnu.org/licenses/agpl-3.0.txt
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the AGPL-3.0 for more details.

import json

import click
from tabulate import tabulate

from superide.registry.client import RegistryClient


@click.command("list", short_help="List published resources")
@click.argument("owner", required=False)
@click.option("--urn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
@click.option("--json-output", is_flag=True)
def access_list_cmd(owner, urn_type, json_output):  # pylint: disable=unused-argument
    reg_client = RegistryClient()
    resources = reg_client.list_resources(owner=owner)
    if json_output:
        return click.echo(json.dumps(resources))
    if not resources:
        return click.secho("You do not have any resources.", fg="yellow")
    for resource in resources:
        click.echo()
        click.secho(resource.get("name"), fg="cyan")
        click.echo("-" * len(resource.get("name")))
        table_data = []
        table_data.append(("URN:", resource.get("urn")))
        table_data.append(("Owner:", resource.get("owner")))
        table_data.append(
            (
                "Access:",
                click.style("Private", fg="red")
                if resource.get("private", False)
                else "Public",
            )
        )
        table_data.append(
            (
                "Access level(s):",
                ", ".join(
                    (level.capitalize() for level in resource.get("access_levels"))
                ),
            )
        )
        click.echo(tabulate(table_data, tablefmt="plain"))
    return click.echo()
