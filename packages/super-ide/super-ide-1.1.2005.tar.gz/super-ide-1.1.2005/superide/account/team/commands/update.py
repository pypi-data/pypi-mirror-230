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

import click

from superide.account.client import AccountClient
from superide.account.validate import validate_orgname_teamname, validate_teamname


@click.command("update", short_help="Update team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
@click.option(
    "--name",
    callback=lambda _, __, value: validate_teamname(value) if value else value,
    help="A new team name",
)
@click.option(
    "--description",
)
def team_update_cmd(orgname_teamname, **kwargs):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    team = client.get_team(orgname, teamname)
    new_team = {
        key: value if value is not None else team[key] for key, value in kwargs.items()
    }
    if not any(kwargs.values()):
        for key in kwargs:
            new_team[key] = click.prompt(key.capitalize(), default=team[key])
            if key == "name":
                validate_teamname(new_team[key])
    client.update_team(orgname, teamname, new_team)
    return click.secho(
        "The team %s has been successfully updated." % teamname,
        fg="green",
    )
