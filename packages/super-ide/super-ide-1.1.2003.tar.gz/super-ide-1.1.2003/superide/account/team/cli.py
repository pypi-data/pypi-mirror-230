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

from superide.account.team.commands.add import team_add_cmd
from superide.account.team.commands.create import team_create_cmd
from superide.account.team.commands.destroy import team_destroy_cmd
from superide.account.team.commands.list import team_list_cmd
from superide.account.team.commands.remove import team_remove_cmd
from superide.account.team.commands.update import team_update_cmd


@click.group(
    "team",
    commands=[
        team_add_cmd,
        team_create_cmd,
        team_destroy_cmd,
        team_list_cmd,
        team_remove_cmd,
        team_update_cmd,
    ],
    short_help="Manage organization teams",
)
def cli():
    pass
