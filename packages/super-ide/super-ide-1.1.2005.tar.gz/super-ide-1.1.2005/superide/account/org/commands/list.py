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

from superide.account.client import AccountClient


@click.command("list", short_help="List organizations and their members")
@click.option("--json-output", is_flag=True)
def org_list_cmd(json_output):
    client = AccountClient()
    orgs = client.list_orgs()
    if json_output:
        return click.echo(json.dumps(orgs))
    if not orgs:
        return click.echo("You do not have any organization")
    for org in orgs:
        click.echo()
        click.secho(org.get("orgname"), fg="cyan")
        click.echo("-" * len(org.get("orgname")))
        data = []
        if org.get("displayname"):
            data.append(("Display Name:", org.get("displayname")))
        if org.get("email"):
            data.append(("Email:", org.get("email")))
        data.append(
            (
                "Owners:",
                ", ".join((owner.get("username") for owner in org.get("owners"))),
            )
        )
        click.echo(tabulate(data, tablefmt="plain"))
    return click.echo()
