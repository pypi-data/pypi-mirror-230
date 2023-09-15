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
from superide.package.meta import PackageSpec, PackageType
from superide.registry.client import RegistryClient


@click.command("unpublish", short_help="Remove a pushed package from the registry")
@click.argument(
    "package", required=True, metavar="[<organization>/]<pkgname>[@<version>]"
)
@click.option(
    "--type",
    type=click.Choice(list(PackageType.items().values())),
    default="library",
    help="Package type, default is set to `library`",
)
@click.option(
    "--undo",
    is_flag=True,
    help="Undo a remove, putting a version back into the registry",
)
def package_unpublish_cmd(package, type, undo):  # pylint: disable=redefined-builtin
    spec = PackageSpec(package)
    response = RegistryClient().unpublish_package(
        owner=spec.owner or AccountClient().get_logged_username(),
        type=type,
        name=spec.name,
        version=str(spec.requirements),
        undo=undo,
    )
    click.secho(response.get("message"), fg="green")
