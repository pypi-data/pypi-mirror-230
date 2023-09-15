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

from superide.registry.access.validate import validate_urn
from superide.registry.client import RegistryClient


@click.command("private", short_help="Make resource private")
@click.argument(
    "urn",
    callback=lambda _, __, value: validate_urn(value),
)
@click.option("--urn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_private_cmd(urn, urn_type):  # pylint: disable=unused-argument
    client = RegistryClient()
    client.update_resource(urn=urn, private=1)
    return click.secho(
        "The resource %s has been successfully updated." % urn,
        fg="green",
    )
