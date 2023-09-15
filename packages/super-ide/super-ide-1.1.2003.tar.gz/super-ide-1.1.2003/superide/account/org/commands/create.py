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
from superide.account.validate import validate_email, validate_orgname


@click.command("create", short_help="Create a new organization")
@click.argument(
    "orgname",
    callback=lambda _, __, value: validate_orgname(value),
)
@click.option(
    "--email", callback=lambda _, __, value: validate_email(value) if value else value
)
@click.option(
    "--displayname",
)
def org_create_cmd(orgname, email, displayname):
    client = AccountClient()
    client.create_org(orgname, email, displayname)
    return click.secho(
        "The organization `%s` has been successfully created." % orgname,
        fg="green",
    )
