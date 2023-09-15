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


@click.command("update", short_help="Update organization")
@click.argument("cur_orgname")
@click.option(
    "--orgname",
    callback=lambda _, __, value: validate_orgname(value) if value else value,
    help="A new orgname",
)
@click.option(
    "--email",
    callback=lambda _, __, value: validate_email(value) if value else value,
)
@click.option("--displayname")
def org_update_cmd(cur_orgname, **kwargs):
    client = AccountClient()
    org = client.get_org(cur_orgname)
    new_org = {
        key: value if value is not None else org[key] for key, value in kwargs.items()
    }
    if not any(kwargs.values()):
        for key in kwargs:
            new_org[key] = click.prompt(key.capitalize(), default=org[key])
            if key == "email":
                validate_email(new_org[key])
            if key == "orgname":
                validate_orgname(new_org[key])
    client.update_org(cur_orgname, new_org)
    return click.secho(
        "The organization `%s` has been successfully updated." % cur_orgname,
        fg="green",
    )
