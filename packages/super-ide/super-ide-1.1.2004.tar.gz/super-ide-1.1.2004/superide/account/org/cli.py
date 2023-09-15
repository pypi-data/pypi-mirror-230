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

from superide.account.org.commands.add import org_add_cmd
from superide.account.org.commands.create import org_create_cmd
from superide.account.org.commands.destroy import org_destroy_cmd
from superide.account.org.commands.list import org_list_cmd
from superide.account.org.commands.remove import org_remove_cmd
from superide.account.org.commands.update import org_update_cmd


@click.group(
    "account",
    commands=[
        org_add_cmd,
        org_create_cmd,
        org_destroy_cmd,
        org_list_cmd,
        org_remove_cmd,
        org_update_cmd,
    ],
    short_help="Manage organizations",
)
def cli():
    pass
