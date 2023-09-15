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

from superide.registry.access.validate import validate_client, validate_urn
from superide.registry.client import RegistryClient


@click.command("grant", short_help="Grant access")
@click.argument("level", type=click.Choice(["admin", "maintainer", "guest"]))
@click.argument(
    "client",
    metavar="[<ORGNAME:TEAMNAME>|<USERNAME>]",
    callback=lambda _, __, value: validate_client(value),
)
@click.argument(
    "urn",
    callback=lambda _, __, value: validate_urn(value),
)
@click.option("--urn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_grant_cmd(level, client, urn, urn_type):  # pylint: disable=unused-argument
    reg_client = RegistryClient()
    reg_client.grant_access_for_resource(urn=urn, client=client, level=level)
    return click.secho(
        "Access for resource %s has been granted for %s" % (urn, client),
        fg="green",
    )
