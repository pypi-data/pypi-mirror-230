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

from superide.package.commands.exec import package_exec_cmd
from superide.package.commands.install import package_install_cmd
from superide.package.commands.list import package_list_cmd
from superide.package.commands.outdated import package_outdated_cmd
from superide.package.commands.pack import package_pack_cmd
from superide.package.commands.publish import package_publish_cmd
from superide.package.commands.search import package_search_cmd
from superide.package.commands.show import package_show_cmd
from superide.package.commands.uninstall import package_uninstall_cmd
from superide.package.commands.unpublish import package_unpublish_cmd
from superide.package.commands.update import package_update_cmd


@click.group(
    "pkg",
    commands=[
        package_exec_cmd,
        package_install_cmd,
        package_list_cmd,
        package_outdated_cmd,
        package_pack_cmd,
        package_publish_cmd,
        package_search_cmd,
        package_show_cmd,
        package_uninstall_cmd,
        package_unpublish_cmd,
        package_update_cmd,
    ],
    short_help="Unified Package Manager",
)
def cli():
    pass
