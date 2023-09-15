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


@click.command("password", short_help="Change password")
@click.option("--old-password", prompt=True, hide_input=True)
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True)
def account_password_cmd(old_password, new_password):
    client = AccountClient()
    client.change_password(old_password, new_password)
    click.secho("Password successfully changed!", fg="green")
