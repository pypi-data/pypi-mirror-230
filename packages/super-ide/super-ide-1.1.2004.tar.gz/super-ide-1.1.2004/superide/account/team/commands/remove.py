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
from superide.account.validate import validate_orgname_teamname


@click.command("remove", short_help="Remove a member from team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
@click.argument("username")
def team_remove_cmd(orgname_teamname, username):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    client.remove_team_member(orgname, teamname, username)
    return click.secho(
        "The %s member has been successfully removed from the %s team."
        % (username, teamname),
        fg="green",
    )
