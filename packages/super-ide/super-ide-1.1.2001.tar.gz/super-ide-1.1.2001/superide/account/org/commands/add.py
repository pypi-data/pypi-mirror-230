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


@click.command("add", short_help="Add a new owner to organization")
@click.argument(
    "orgname",
)
@click.argument(
    "username",
)
def org_add_cmd(orgname, username):
    client = AccountClient()
    client.add_org_owner(orgname, username)
    return click.secho(
        "The new owner `%s` has been successfully added to the `%s` organization."
        % (username, orgname),
        fg="green",
    )
