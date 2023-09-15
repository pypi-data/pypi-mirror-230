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


@click.command("remove", short_help="Remove an owner from organization")
@click.argument(
    "orgname",
)
@click.argument(
    "username",
)
def org_remove_cmd(orgname, username):
    client = AccountClient()
    client.remove_org_owner(orgname, username)
    return click.secho(
        "The `%s` owner has been successfully removed from the `%s` organization."
        % (username, orgname),
        fg="green",
    )
