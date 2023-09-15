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

from superide.registry.access.commands.grant import access_grant_cmd
from superide.registry.access.commands.list import access_list_cmd
from superide.registry.access.commands.private import access_private_cmd
from superide.registry.access.commands.public import access_public_cmd
from superide.registry.access.commands.revoke import access_revoke_cmd


@click.group(
    "access",
    commands=[
        access_grant_cmd,
        access_list_cmd,
        access_private_cmd,
        access_public_cmd,
        access_revoke_cmd,
    ],
    short_help="Manage resource access",
)
def cli():
    pass
