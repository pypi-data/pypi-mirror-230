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

from superide.account.commands.destroy import account_destroy_cmd
from superide.account.commands.forgot import account_forgot_cmd
from superide.account.commands.login import account_login_cmd
from superide.account.commands.logout import account_logout_cmd
from superide.account.commands.password import account_password_cmd
from superide.account.commands.register import account_register_cmd
from superide.account.commands.show import account_show_cmd
from superide.account.commands.token import account_token_cmd
from superide.account.commands.update import account_update_cmd


@click.group(
    "account",
    commands=[
        account_destroy_cmd,
        account_forgot_cmd,
        account_login_cmd,
        account_logout_cmd,
        account_password_cmd,
        account_register_cmd,
        account_show_cmd,
        account_token_cmd,
        account_update_cmd,
    ],
    short_help="Manage superide account",
)
def cli():
    pass
